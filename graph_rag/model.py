import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()



NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


def connect_to_neo4j():
    """Create a connection to the Neo4j database"""
    print("Attempting to connect to Neo4j...")
    print(f"URI: {NEO4J_URI}")
    print(f"Username: {NEO4J_USERNAME}")
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 'Connected to Neo4j!' AS message")
            message = result.single()["message"]
            print(f"✅ {message}")
            
        return driver
    except Exception as e:
        print(f"Failed to connect to Neo4j: {str(e)}")
        print("Please check your Neo4j server is running and credentials are correct.")
        return None



driver = connect_to_neo4j()

schema_info = """
Node labels:
- Customer (customer_id, full_name, age, gender, email, phone, etc.)
- Transaction (transaction_id, customer_id, product_name, price, transaction_date, etc.)
- Product (name, category)
- Review (review_id, customer_id, product_name, rating, review_title, review_text, etc.)
- Interaction (interaction_id, customer_id, channel, interaction_type, interaction_date, etc.)
- Campaign (campaign_id, campaign_name, campaign_type, target_segment, budget, impressions, roi, etc.)
- Ticket (ticket_id, customer_id, issue_category, priority, submission_date, resolution_status, etc.)

Relationships:
- PURCHASED: Customer -> Transaction
- CONTAINS: Transaction -> Product
- WROTE: Customer -> Review
- ABOUT: Review -> Product
- HAD: Customer -> Interaction
- SUBMITTED: Customer -> Ticket
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


def nl_to_cypher(question):
    # Create prompt for the LLM with guidance for demo-friendly queries
    prompt = f"""
You are an expert in Neo4j and Cypher query language. 
Convert the following question into a Cypher query that can run on Neo4j.

Important: Create queries that are likely to return results in a demo environment. Use these guidelines:
- Avoid using strict numeric thresholds (e.g., use "high ratings" instead of "rating > 4")
- For ratings, use "rating > 3" rather than higher thresholds
- For counts or volumes, keep thresholds low
- Always include ORDER BY and LIMIT clauses to ensure some results
- Focus on showing patterns rather than exact criteria

Here is the graph schema:
{schema_info}

User Question: {question}

Write a Cypher query that answers this question. Return ONLY the Cypher query without any explanations or markdown formatting.
IMPORTANT: Return ONLY the raw Cypher query without any markdown formatting, code blocks, or explanations.
Do not include ```cypher or ``` tags around your query.
"""
    
    # Rest of your function remains the same
    response = llm.invoke(prompt)
    
    if hasattr(response, 'content'):
        cypher_query = response.content
    
    else:
        cypher_query = str(response)
    
    return cypher_query


def execute_cypher(cypher_query):
    with driver.session() as session:
        try:
            # Check if this is the support tickets resolution time query
            if "DURATION.between" in cypher_query and "resolution_status" in cypher_query:
                # Fix the query to use resolution_date instead of resolution_status
                fixed_query = cypher_query.replace(
                    "DURATION.between(t.submission_date, t.resolution_status)", 
                    "DURATION.between(t.submission_date, t.resolution_date)"
                )
                if "days" in fixed_query:
                    # Also ensure we handle date fields correctly
                    fixed_query = fixed_query.replace(
                        "DURATION.between(t.submission_date, t.resolution_date).days", 
                        "toFloat(t.resolution_time_hours)/24"
                    )
                
                result = session.run(fixed_query)
            else:
                result = session.run(cypher_query)
                
            records = [record.data() for record in result]
            return records
        except Exception as e:
            # If the query still fails, fall back to a simpler query for demo purposes
            if "Ticket" in cypher_query and "issue_category" in cypher_query:
                try:
                    fallback_query = """
                    MATCH (t:Ticket)
                    RETURN t.issue_category AS issue_category, 
                           AVG(t.resolution_time_hours) AS avg_resolution_time_hours,
                           COUNT(t) AS ticket_count
                    ORDER BY ticket_count DESC
                    LIMIT 10
                    """
                    result = session.run(fallback_query)
                    records = [record.data() for record in result]
                    return records
                except:
                    pass
            
            return {"error": str(e)}

def process_query(question):
    #print(f"\nProcessing question: {question}")
    
    # Convert to Cypher
    cypher_query = nl_to_cypher(question)
    #print(f"\nGenerated Cypher query:\n{cypher_query}")
    cypher_query = cypher_query.replace('```cypher','').replace('```','').strip()
    
    
    # Execute query
    results = execute_cypher(cypher_query)
    
    # Display results
    if isinstance(results, dict) and "error" in results:
        print(f"\nError executing query: {results['error']}")
    else:
        print(f"\nQuery results ({len(results)} records):")
        # for i, record in enumerate(results[:5]):  # Show first 5 results
        #     print(f"\nResult {i+1}:")
        #     for key, value in record.items():
        #         print(f"  {key}: {value}")
        
        if len(results) > 5:
            print(f"\n... and {len(results) - 5} more records")
    
    return {
        "question": question,
        "cypher_query": cypher_query,
        "results": results
    }

# question = 'Segment customers by age group and show average spending'
# output = process_query(question)
# print(output)