#!/usr/bin/env python3
"""
Sequential Multi-Agent Opportunity Finder
Runs 3 Zo agents sequentially to research pain points and opportunities for Dioni
"""
import requests
import os
import json
from datetime import datetime

def spawn_agent(agent_name, prompt):
    """Spawn a single Zo agent with a specific research focus"""
    print(f"\n{'='*80}")
    print(f"🚀 Spawning {agent_name}...")
    print('='*80)
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=600  # 10 min timeout
        )
        result = response.json()
        return {
            "agent": agent_name,
            "output": result.get("output", ""),
            "success": True
        }
    except Exception as e:
        return {
            "agent": agent_name,
            "output": f"Error: {str(e)}",
            "success": False
        }

def main():
    print("="*80)
    print("MULTI-AGENT OPPORTUNITY FINDER FOR DIONI VASQUEZ")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRunning 3 research agents sequentially...\n")
    
    # Agent 1: Pain Point Hunter
    agent1_prompt = """You are a PAIN POINT HUNTER agent.

Your mission: Scrape and research the TOP pain points people are complaining about across:
- Reddit (r/entrepreneur, r/SaaS, r/startups, r/webdev, r/productivity, r/gaming, r/technology)
- Twitter/X (search for "I hate when", "why is there no", "wish there was")
- Product Hunt comments
- Hacker News discussions

Search for patterns in:
1. Recurring complaints (mentioned 10+ times)
2. Problems people are WILLING TO PAY to solve
3. Technical pain points that developers face
4. Creative/gaming/content creation frustrations
5. Underserved niches

Output format:
- Top 10 pain points ranked by frequency + monetization potential
- Include specific quotes from real people
- Note which platforms each pain point appears on most
- Estimate market size for each

Be thorough. Use web_search, x_search, and web_research aggressively."""

    result1 = spawn_agent("Pain Point Hunter", agent1_prompt)
    print(result1['output'])
    
    # Agent 2: Dioni Researcher
    agent2_prompt = """You are a PERSONAL RESEARCH agent.

Your mission: Research EVERYTHING about Dioni Vasquez to understand his:
- Skills (coding, music production, content creation, etc.)
- Interests (gaming, crypto, AI, spatial audio, multiplayer games)
- Past projects (spatial-worlds, isometric games, NFT scanner, etc.)
- Social presence (Twitter/X @dioniproduces, GitHub dioniproduces, etc.)
- Work style (vibe coding, fast iteration, autonomous building)
- Technical stack (Phaser, Bun, TypeScript, Python, Zo, etc.)

Search for:
1. His GitHub repos and commit patterns
2. Twitter posts to understand his vibe and interests
3. Any public profiles or portfolios
4. His Zo workspace Skills folder for project insights
5. Comments or posts he's made online

Check his workspace at /home/workspace/Skills to see what he's been building.

Output format:
- Comprehensive profile of Dioni's skills, interests, and style
- What he's uniquely positioned to build
- What would make him have FUN while building
- What aligns with his "vibe coding" philosophy
- His competitive advantages

Use web_search, x_search, grep_search, and list_files."""

    result2 = spawn_agent("Dioni Researcher", agent2_prompt)
    print(result2['output'])
    
    # Agent 3: Strategic Synthesizer & Debater
    agent3_prompt = f"""You are a STRATEGIC SYNTHESIZER & DEBATER agent.

You have the research from two other agents:

PAIN POINTS FOUND:
{result1['output'][:3000]}...

DIONI'S PROFILE:
{result2['output'][:3000]}...

Your mission:
1. Cross-reference pain points with Dioni's unique skills
2. Identify TOP 5 opportunities where his interests + skills + market demand align PERFECTLY
3. For each opportunity, DEBATE WITH YOURSELF:
   - Why this is perfect for Dioni
   - Why this could fail
   - Revenue potential (be realistic)
   - Time to build (hours/days/weeks)
   - Fun factor (1-10)
   - Competitive advantage
4. Check assumptions rigorously - call out when something seems too good to be true
5. Rank the final opportunities by: Revenue Potential × Fun Factor × Speed to Market

Also do additional research on:
- What's making money RIGHT NOW in 2026 (search for recent success stories)
- Viral product launches in the last month
- What tools/platforms are trending

Output format:
- Rigorous debate on each opportunity (pros/cons)
- Final TOP 3 RECOMMENDATIONS with clear action steps
- "Just start building X right now" - be decisive
- Include tech stack, timeline, and first milestone

Use web_search with time_range="week" for current trends."""

    result3 = spawn_agent("Strategic Synthesizer", agent3_prompt)
    print(result3['output'])
    
    # Save all results
    results = [result1, result2, result3]
    output_file = f"/home/workspace/opportunity_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\n{'='*80}")
    print(f"💾 Full results saved to: {output_file}")
    print(f"✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*80)

if __name__ == "__main__":
    main()
