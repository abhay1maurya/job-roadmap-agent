# agent.py

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

class RoadmapGenerator:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
    
    def search_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Extract relevant information
            results = []
            
            # Abstract from DuckDuckGo
            if data.get('Abstract'):
                results.append(data['Abstract'])
            
            # Related topics
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:  # Limit to first 3 topics
                    if 'Text' in topic:
                        results.append(topic['Text'])
            
            # If no results found, return a generic response
            if not results:
                return f"Search for '{query}' didn't return specific results. Using standard interview process."
            
            return " ".join(results)[:1500]  # Limit length
            
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
            return f"Search unavailable. Using standard interview process for the role."
    
    def search_company_info(self, company: str, role: str) -> str:
        """Search for company-specific interview information using DuckDuckGo"""
        print(f"🔍 Searching DuckDuckGo for {company} {role} interview process...")
        
        queries = [
            f"{company} {role} interview process",
            f"{company} technical interview questions {role}",
            f"{company} hiring process {role}",
            f"how to prepare for {company} {role} interview"
        ]
        
        all_results = []
        for query in queries[:2]:  # Use first 2 queries to avoid too many requests
            try:
                result = self.search_duckduckgo(query)
                if result and "didn't return specific results" not in result:
                    all_results.append(result)
            except Exception as e:
                print(f"⚠️ Query '{query}' failed: {e}")
        
        if all_results:
            combined_results = " ".join(all_results)
            return combined_results[:2000]  # Limit total length
        
        # Fallback information
        return f"""
        Standard interview process for {role} positions at {company}. 
        Typically includes:
        - Technical screening round with coding questions
        - System design discussion for mid-level and above roles
        - Behavioral and cultural fit interviews
        - Possible take-home assignment or live coding session
        
        Focus on data structures, algorithms, and company-specific technologies.
        """
    
    def extract_json_from_text(self, text: str) -> dict:
        """Extract JSON from LLM response"""
        try:
            # Clean the text
            cleaned = text.strip()
            
            # Try to find JSON in code blocks
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            # Find the first { and last }
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = cleaned[start:end]
                return json.loads(json_str)
            else:
                # Try to parse the whole text as JSON
                return json.loads(cleaned)
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {text[:500]}...")
            # Return default structure
            return self.create_default_roadmap("Unknown", "Unknown")
    
    def generate_roadmap(self, company: str, role: str, jd_text: str) -> dict:
        """Generate interview preparation roadmap"""
        print(f"🎯 Generating roadmap for {role} at {company}...")
        
        # Step 1: Get company insights
        print("🌐 Gathering company information from DuckDuckGo...")
        company_info = self.search_company_info(company, role)
        
        # Step 2: Create prompt
        prompt_text = f"""
        Create a comprehensive interview preparation roadmap based on the job description and company information.
        
        COMPANY: {company}
        ROLE: {role}
        
        JOB DESCRIPTION:
        {jd_text}
        
        COMPANY INTERVIEW INFO:
        {company_info}
        
        Please provide a structured roadmap in JSON format with these exact fields:
        - company: Company name
        - role: Job role  
        - rounds: List of 3-5 interview rounds, each with "type" and "topics" (list of 3-5 topics per round)
        - difficulty: Overall difficulty (Easy, Medium, Hard, Very Hard)
        - recommended_order: Suggested study order of main topics
        - evidence: Object with "key_skills" (from JD) and "topic_count"
        
        Return ONLY valid JSON without any additional text, comments, or explanations.
        
        Example format:
        {{
            "company": "Google",
            "role": "SDE1",
            "rounds": [
                {{"type": "Technical Screening", "topics": ["Data Structures", "Algorithms", "Problem Solving"]}},
                {{"type": "Coding Round", "topics": ["System Design", "Object-Oriented Programming", "API Design"]}},
                {{"type": "System Design", "topics": ["Microservices", "Scalability", "Database Design"]}},
                {{"type": "Behavioral", "topics": ["Teamwork", "Communication", "Leadership"]}}
            ],
            "difficulty": "Hard",
            "recommended_order": ["Data Structures", "Algorithms", "System Design", "Behavioral"],
            "evidence": {{
                "key_skills": ["Python", "AWS", "Docker"],
                "topic_count": 4
            }}
        }}
        """
        
        print("🧠 Generating roadmap with AI...")
        try:
            response = self.llm.invoke([HumanMessage(content=prompt_text)])
            response_text = response.content
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            # Return default roadmap
            return self.create_default_roadmap(company, role)
        
        # Parse the response
        roadmap = self.extract_json_from_text(response_text)
        
        # Ensure company and role are set correctly
        roadmap["company"] = company
        roadmap["role"] = role
        
        # Add metadata
        roadmap["generated_at"] = datetime.now().isoformat()
        roadmap["version"] = "1.0"
        
        print("✅ Roadmap generated successfully!")
        return roadmap
    
    def create_default_roadmap(self, company: str, role: str) -> dict:
        """Create a default roadmap when AI generation fails"""
        return {
            "company": company,
            "role": role,
            "rounds": [
                {"type": "Technical Screening", "topics": ["Data Structures", "Algorithms", "Problem Solving"]},
                {"type": "Coding Round", "topics": ["System Design", "Object-Oriented Programming"]},
                {"type": "System Design", "topics": ["Microservices", "Scalability", "Database Design"]},
                {"type": "Behavioral", "topics": ["Teamwork", "Communication", "Experience"]}
            ],
            "difficulty": "Medium",
            "recommended_order": ["Data Structures", "Algorithms", "System Design", "Behavioral"],
            "evidence": {
                "key_skills": ["General Programming", "Problem Solving"],
                "topic_count": 4
            },
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "note": "Default roadmap - AI generation failed"
        }
    
    def save_roadmap(self, roadmap: dict, company: str, role: str):
        """Save roadmap to JSON file"""
        filename = f"{company}_{role}_roadmap.json".replace(" ", "_").replace("/", "_").lower()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Roadmap saved as: {filename}")
        return filename
    
    def display_roadmap(self, roadmap: dict):
        """Display roadmap in a readable format"""
        print("\n" + "="*60)
        print("📊 ROADMAP SUMMARY")
        print("="*60)
        print(f"🏢 Company: {roadmap.get('company', 'N/A')}")
        print(f"💼 Role: {roadmap.get('role', 'N/A')}")
        print(f"🎯 Difficulty: {roadmap.get('difficulty', 'N/A')}")
        print(f"🔄 Total Rounds: {len(roadmap.get('rounds', []))}")
        
        print("\n🔄 Interview Rounds:")
        for i, round_info in enumerate(roadmap.get('rounds', []), 1):
            round_type = round_info.get('type', 'Unknown')
            topics = ', '.join(round_info.get('topics', []))
            print(f"  {i}. {round_type}")
            print(f"     📚 Topics: {topics}")
        
        print(f"\n📖 Recommended Study Order: {', '.join(roadmap.get('recommended_order', []))}")
        
        evidence = roadmap.get('evidence', {})
        if evidence:
            print(f"🔍 Key Skills from JD: {', '.join(evidence.get('key_skills', []))}")
        
        if roadmap.get('note'):
            print(f"💡 Note: {roadmap.get('note')}")
        
        print("="*60)

def get_job_description():
    """Get job description from user input"""
    print("\nPlease paste the job description:")
    print("(Enter your job description below. Press Ctrl+Z then Enter when finished on Windows)")
    print("="*50)
    
    jd_lines = []
    try:
        while True:
            try:
                line = input()
                jd_lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    except:
        pass
    
    jd_text = "\n".join(jd_lines)
    
    if not jd_text.strip():
        print("❌ Error: Job description cannot be empty.")
        return None
    
    return jd_text

def main():
    """Main function to run the roadmap generator"""
    
    # Check API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Please set GOOGLE_API_KEY in your .env file")
        print("   Get it from: https://aistudio.google.com/app/apikey")
        return
    
    # Get user input
    print("🚀 Job Preparation Roadmap Generator")
    print("="*50)
    
    # Get company name (mandatory)
    while True:
        company = input("Enter company name: ").strip()
        if company:
            break
        print("❌ Company name is required. Please enter a company name.")
    
    # Get job role (mandatory)
    while True:
        role = input("Enter job role: ").strip()
        if role:
            break
        print("❌ Job role is required. Please enter a job role.")
    
    # Get job description (mandatory)
    jd_text = get_job_description()
    if jd_text is None:
        return
    
    # Generate roadmap
    generator = RoadmapGenerator()
    
    try:
        roadmap = generator.generate_roadmap(company, role, jd_text)
        generator.display_roadmap(roadmap)
        
        # Save to file
        filename = generator.save_roadmap(roadmap, company, role)
        print(f"\n✅ Complete! Roadmap saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error generating roadmap: {e}")

if __name__ == "__main__":
    main()