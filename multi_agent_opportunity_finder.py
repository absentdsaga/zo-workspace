#!/usr/bin/env python3
"""
Multi-Agent Opportunity Finder
Spawns 3 parallel Zo agents to research pain points and opportunities for Dioni
"""
import asyncio
import aiohttp
import os
import json
from datetime import datetime

async def spawn_agent(session, agent_name, prompt):
    """Spawn a single Zo agent with a specific research focus"""
    print(f"\n🚀 Spawning {agent_name}...")
    
    try:
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=aiohttp.ClientTimeout(total=600)  # 10 min timeout
        ) as resp:
            result = await resp.json()
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

async def main():
    print("="*80)
    print("MULTI-AGENT OPPORTUNITY FINDER FOR DIONI VASQUEZ")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSpawning 3 parallel research agents...\n")
    
    # Agent 1: Pain Point Hunter
    agent1_prompt = """You are a PAIN POINT HUNTER agent.

Your mission: Scrape and research the TOP pain points people are complaining about across:
- Reddit (r/entrepreneur, r/SaaS, r/startups, r/webdev, r/productivity, r/gaming, r/technology)
- Twitter/X (search for "I hate when", "why is there no", "wish there was")
- Product Hunt comments
- Hacker News discussions
- YouTube comments on tech/productivity videos

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

    # Agent 2: Dioni Researcher
    agent2_prompt = """You are a PERSONAL RESEARCH agent.

Your mission: Research EVERYTHING about Dioni Vasquez to understand his:
- Skills (coding, music production, content creation, etc.)
- Interests (gaming, crypto, AI, spatial audio, multiplayer games)
- Past projects (spatial-worlds, isometric games, NFT scanner, etc.)
- Social presence (Twitter, GitHub, YouTube if available)
- Work style (vibe coding, fast iteration, autonomous building)
- Technical stack (Phaser, Bun, TypeScript, Python, Zo, etc.)

Search for:
1. His GitHub repos and commit patterns
2. Twitter posts to understand his vibe and interests
3. Any public profiles or portfolios
4. Skills folder in his Zo workspace for project insights
5. Comments or posts he's made online

Output format:
- Comprehensive profile of Dioni's skills, interests, and style
- What he's uniquely positioned to build
- What would make him have FUN while building
- What aligns with his "vibe coding" philosophy
- His competitive advantages

Use web_search, x_search, and read his workspace files."""

    # Agent 3: Strategic Synthesizer
    agent3_prompt = """You are a STRATEGIC SYNTHESIZER agent.

Your mission: After the other two agents finish, you will:
1. Cross-reference pain points with Dioni's unique skills
2. Identify opportunities where his interests + skills + market demand align
3. Debate with yourself on each opportunity (pros/cons)
4. Check assumptions rigorously

For now, do preliminary research on:
- Current trending opportunities in AI agents, gaming, creative tools
- What's making money RIGHT NOW (search for "made $X with", revenue reports)
- Underserved markets with low competition
- Viral product launches in the last 3 months
- SaaS ideas that are working in 2026

Output format:
- Top 5 trending opportunity categories
- Recent success stories with revenue data
- Gaps in the market
- What's oversaturated vs underserved

Use web_search with time_range="week" and web_research aggressively."""

    agents = [
        ("Pain Point Hunter", agent1_prompt),
        ("Dioni Researcher", agent2_prompt),
        ("Strategic Synthesizer", agent3_prompt)
    ]
    
    # Spawn all agents in parallel
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[
            spawn_agent(session, name, prompt) 
            for name, prompt in agents
        ])
    
    # Print results
    print("\n" + "="*80)
    print("AGENT RESULTS")
    print("="*80)
    
    for result in results:
        print(f"\n{'='*80}")
        print(f"📊 {result['agent'].upper()}")
        print('='*80)
        if result['success']:
            print(result['output'])
        else:
            print(f"❌ Agent failed: {result['output']}")
    
    # Save to file
    output_file = f"/home/workspace/opportunity_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\n💾 Full results saved to: {output_file}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
