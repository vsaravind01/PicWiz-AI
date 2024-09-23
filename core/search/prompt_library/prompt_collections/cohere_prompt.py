SEMANTIC_PARSING = """Parse the following search query into a structured format that includes entities (including person names) and a MongoDB-like boolean query:

Query: {query}

Output a Python dictionary with the following structure:
{{
    "entities": {{
        "people": [list of entities mentioned in the query, including person names],
        "objects": [list of objects mentioned in the query],
        "locations": [list of locations mentioned in the query]
    }},
    "query": {{MongoDB-like query structure}}
}}

Rules:
1. Identify all entities (objects, people, actions, places) mentioned in the query, including person names.
2. Replace any first-person context (e.g., "me", "my", "I") with the tag <me>.
3. Create a MongoDB-like query using $and, $or, and $not operators based on the query's boolean logic.
4. For "NOT" relationships, use the $not operator.
5. If a query mentions "with" or "without", treat it as $and or $not respectively.
6. Understand the query as a whole and not just the individual words and then create the query.

Examples:
1. Query: "Find photos of John and Sarah at the beach"
   Output: {{
       "entities": {{
           "people": ["John", "Sarah"],
           "objects": [],
           "locations": ["beach"]
       }},
       "query": {{
           "$and": [
               {{"entities": "John"}},
               {{"entities": "Sarah"}},
               {{"entities": "beach"}}
           ]
       }}
   }}

2. Query: "Show me pictures of myself with dogs but not cats"
   Output: {{
       "entities": {{
           "people": ["<me>"],
           "objects": ["dogs", "cats"]
           "locations": []
       }},
       "query": {{
           "$and": [
               {{"entities": "<me>"}},
               {{"entities": "dogs"}},
               {{"$not": {{"entities": "cats"}}}}
           ]
       }}
   }}

3. Query: "Find photos of my sister or my brother"
   Output: {{
       "entities": {{
           "people": ["<me>", "sister", "brother"],
           "objects": [],
           "locations": []
       }},
       "query": {{
           "$or": [
               {{"$and": [{{"entities": "<me>"}}, {{"entities": "sister"}}]}},
               {{"$and": [{{"entities": "<me>"}}, {{"entities": "brother"}}]}}
           ]
       }}
   }}

Now, parse the following query:
{query}

Output:"""

SIMILAR_QUERY = """Generate {k} very similar search queries with alternate words to the following query, ignore all the person names and first-person context.
If any person names are mentioned, just describe them as people or human. Give more importance to the objects, actions and places in the queries. In each query, try to pick a different
an alternate name for the same object, action or place, but keep the exact same intent and context.

Provide your output in JSON format:
{{
    "similar_queries": [list of similar queries]
}}

Query: {query}
"""
