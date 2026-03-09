Project Overview
This project is a Django 6 REST API for managing companies and their performance scores.
App: serviceApp
Core models:
Company: base company profile (industry, state, revenue, etc.).
CompanyScore: precomputed performance score and rank for each company.
Use case:
Efficiently list “top” companies filtered by industry/state.
Fetch a single company’s details along with its score and rank.
All ranking is done at the database level to scale to large datasets (e.g. 100k+ companies).
Setup
Prerequisites
Python 3.10+
pip
(Optional) virtualenv or venv
SQLite (bundled with Python)
Git
1. Clone and install dependencies
git clone <YOUR_REPO_URL> "vasalys media task"cd "vasalys media task"python -m venv venvvenv\Scripts\activate  # on Windows# source venv/bin/activate  # on macOS/Linuxpip install -r requirements.txt
2. Apply migrations
From the myapp directory:
cd myapppython manage.py migrate
3. Populate sample data (companies, scores, ranks)
There is a custom management command that:
Bulk-creates 100,000 Company rows.
Calculates total_score for each company.
Assigns rank at the database level.
Run:
python manage.py script
> This may take a bit of time due to the volume (100k rows), but it uses bulk operations and DB-level ranking to keep it reasonably fast.
4. Run the development server
python manage.py runserver
The API will be available at http://127.0.0.1:8000/.
Data Model
Company
Located in serviceApp/models/companyModel.py.
Key fields:
name: CharField(max_length=50)
industry: CharField(max_length=100)
state: CharField(max_length=100)
annual_revenue: IntegerField
employee_count: IntegerField
compliance_score: numeric score (0–100, with validation)
is_active: BooleanField (default True)
create_at: DateTimeField(auto_now_add=True)
Indexes (see “Database Indexes” below):
industry_idx on industry
annual_revenue_idx on annual_revenue
is_active_idx on is_active
CompanyScore
Located in serviceApp/models/companyScoreModel.py.
Key fields:
company: ForeignKey → Company
total_score: numeric score in \[0, 100\], based on revenue and compliance
rank: integer rank (1 = best). Same score gets same rank.
calculated_at: DateTimeField(auto_now_add=True)
Indexes:
total_score_idx on total_score
rank_idx on rank
Score Calculation
Defined in serviceApp/utils.py:
Revenue component: revenue_score = min(annual_revenue / 1_000_000, 100)
Compliance component: compliance_score as stored on Company
Weighted total:
total_score
=
0.6
⋅
revenue_score
+
0.4
⋅
compliance_score
total_score=0.6⋅revenue_score+0.4⋅compliance_score
This computation is done once per company when running the script management command, and stored in CompanyScore.total_score.
Database Indexes and Why They Exist
On Company
industry_idx (industry)
Used when filtering by industry in the “top companies” endpoint:
Company.objects.filter(industry=industry, state=state, ...)
Significantly speeds up queries like “top companies for industry X”.
annual_revenue_idx (annual_revenue)
Useful for analytical or reporting queries where you filter/sort by revenue.
Can also help if you later add endpoints that query companies by revenue thresholds.
is_active_idx (is_active)
Useful for queries that only consider active companies:
e.g. Company.objects.filter(is_active=True, ...)
Keeps “active only” queries fast, even on large tables.
On CompanyScore
total_score_idx (total_score)
Critical for ranking and “top N” queries.
Used when ordering by score (descending) to get best companies quickly.
rank_idx (rank)
Speeds up queries like “top 10 companies by rank”:
CompanyScore.objects.order_by('rank')[:10]
Also useful to quickly jump to ranges of ranks.
Overall, these indexes ensure:
Fast filters by industry and state.
Fast ordered queries by total_score or rank.
Good performance even with 100k+ rows.
Ranking Logic (Database Level)
Requirement: “Same score should receive the same rank. Ranking must be done at database level.”
Concept
We use dense ranking over total_score (descending):
If scores are [100, 100, 99, 98, 98], ranks are [1, 1, 2, 3, 3].
This is implemented using SQL window functions (e.g. DENSE_RANK()) or Django’s Window/DenseRank expressions.
Once computed, the rank is stored in CompanyScore.rank so API reads are cheap.
Workflow in the management command
In serviceApp/management/commands/script.py:
Generate Companies:
Uses bulk_create in chunks of 10,000 to efficiently insert 100,000 Company records inside an atomic transaction.
Insert Company Scores:
For each Company, calls calculate_company_score(company) from utils.py.
Creates a corresponding CompanyScore row.
Assign Ranks (DB-Level):
Uses a DB query leveraging window functions (e.g. DENSE_RANK() OVER (ORDER BY total_score DESC)) to compute ranks.
Updates rank for all rows in one or a few SQL statements, not per-row Python loops.
Guarantees:
Same total_score → same rank.
Rankings are deterministic and efficient.
> If underlying data changes, you can rerun the rank computation step (or the entire script command) to refresh rank.
API Endpoints
1) GET /api/companies/top
Purpose: Retrieve top companies filtered by industry and state, including score and rank.
Query parameters:
industry (required): exact industry match.
state (required): exact state match.
limit (optional): maximum number of companies to return.
Example:
GET /api/companies/top?industry=Industry99999&state=State99999&limit=50
Behavior:
Filters Company by industry and state.
Uses CompanyListSerializer to include:
id, name, industry, state, annual_revenue
total_score and rank (fetched from related CompanyScore).
Returns 404 if no companies match the filter.
Uses DB indexes on industry (and can leverage total_score_idx/rank_idx if you sort by score/rank).
2) GET /api/companies/<id>/
Purpose: Retrieve a single company’s full details, including its score and rank.
Example:
GET /api/companies/123/
Behavior:
Fetches Company by primary key (id).
Uses CompanyDetailSerializer to include:
Company fields (e.g. name, industry, state, annual_revenue, employee_count, compliance_score).
total_score and rank from CompanyScore.
Returns 404 if the company does not exist.
If no CompanyScore exists for that company, total_score and rank can be null (depending on serializer implementation).
Performance and Optimization Notes
Bulk inserts:
Companies are created via bulk_create in chunks of 10,000, significantly reducing insert overhead.
Wrapped in transaction.atomic() for consistency and performance.
Precomputed scores and ranks:
total_score and rank are materialized in CompanyScore.
API requests do simple lookups instead of recomputing scores/ranks on the fly.
Database indexes:
Carefully chosen indexes on Company and CompanyScore support:
Filter by industry, state, is_active.
Sort/filter by total_score and rank.
Essential for large data volumes (100k+).
DB-level ranking:
Ranking logic uses SQL window functions (or equivalent DB queries) to assign rank in a single DB pass, avoiding Python-side O(n log n)/O(n^2) logic.
Ensures same total_score gets identical rank (dense ranking).
Serializer design:
CompanyListSerializer and CompanyDetailSerializer fetch total_score/rank from CompanyScore, keeping response shapes consistent across list and detail endpoints.
