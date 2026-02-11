#!/usr/bin/env python3
"""
True Multi-Agent Debate System
Spawns 3 independent Zo agents with different perspectives to debate Dioni's opportunities
"""
import requests
import os
import json
from datetime import datetime
import time

def ask_zo(prompt, agent_name):
    """Call the /zo/ask API to spawn an independent agent"""
    print(f"\n{'='*80}")
    print(f"🤖 Spawning: {agent_name}")
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
        output = result.get("output", "")
        
        print(f"✅ {agent_name} completed")
        print(f"Output length: {len(output)} characters")
        
        return {
            "agent": agent_name,
            "output": output,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ {agent_name} failed: {str(e)}")
        return {
            "agent": agent_name,
            "output": f"Error: {str(e)}",
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("="*80)
    print("TRUE MULTI-AGENT DEBATE SYSTEM")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRunning 3 independent Zo agents sequentially...\n")
    
    # Load Dioni's context
    dioni_context = """
DIONI VASQUEZ PROFILE:

**Background:**
- Oscar-nominated Executive Creative Producer (HBO's Welcome to Chechnya)
- Emmy, Peabody, BAFTA, Cannes Lions winner
- Generated $750M+ in client revenue for Meta, HBO, American Express, Cadillac, Walmart, Starbucks, Planet Fitness
- Built content engines: 5M+ subscribers, 2B+ views, 500M+ YouTube views
- 15+ years experience as founder of One Push Digital Creative

**Key Achievements:**
1. Planet Fitness: Fixed fragmented post-production across 16 agencies → 50-60% cost reduction, delivered Super Bowl spots
2. Brat TV & Meta Originals: Built youth IP from 0→5M subscribers, 500M+ views
3. Cadillac XT6 with Spike Lee: 20% sales lift
4. American Express: Saved failing B2B digital program, drove double-digit growth

**Skills:**
- 360° Operator: Creative vision + strategic execution + operational scale + technical fluency
- Framework: Diagnose → Systemize → Execute → Optimize
- Production: Showrunning, budgets (5-8 figures), team leadership, post-production
- Platforms: YouTube, Instagram, TikTok, Snapchat, broadcast/OTT
- Tech: Adobe Suite, Final Cut Pro, DaVinci, Figma, Jira, AI tools

**Current Interests (from Zo workspace):**
- Building on Zo: Spatial Worlds (proximity voice chat + pixel art), isometric game engines
- Multiplayer tech: Real-time sync, WebSockets, spatial audio
- Music production (dioniproduces)
- Crypto/NFTs: Solana NFT scanner
- AI automation: Workflow orchestration, autonomous agents

**Stated Goals:**
- Looking for COO, Head of Product, or VP of Creative & Strategy roles
- Interested in Web3, tech, media, culture intersection
- OR building his own business

**Work Style:**
- "Vibe coding": Fast iteration, ships quickly
- Loves automation and autonomous systems
- Visual aesthetics matter (Chrono Trigger art style)
- Prefers building with Zo (Bun, TypeScript, Python)
"""

    # Agent 1: The Pragmatic Capitalist
    agent1_prompt = f"""You are THE PRAGMATIC CAPITALIST - a ruthlessly practical business advisor.

{dioni_context}

Your mission: Analyze what Dioni should build to maximize revenue in the next 12 months.

Your perspective:
- Track record > ideas (he's proven he can execute at $750M scale)
- Network = unfair advantage (his contacts are worth millions)
- Time is money (he's 15 years in, no time for experiments)
- Recurring revenue > one-time projects
- B2B > B2C (enterprise pays 100x more)

Research and recommend:
1. What opportunity maximizes his existing advantages? (network, track record, skills)
2. What's the fastest path to $100K/month revenue?
3. What can he charge $50K+ for that brands will pay TODAY?
4. Should he build a business or take a COO role? (compare financially)

Be specific with numbers, timelines, and tactics. No fluff.

Output your recommendation in this format:
- OPPORTUNITY: [name]
- WHY: [leverage his advantages]
- REVENUE MODEL: [specific pricing]
- 12-MONTH PROJECTION: [realistic numbers]
- FIRST ACTIONS: [what to do this week]
"""

    # Agent 2: The Visionary Idealist  
    agent2_prompt = f"""You are THE VISIONARY IDEALIST - you care about legacy and impact over money.

{dioni_context}

Your mission: What should Dioni build that he'll be proud of in 10 years?

Your perspective:
- Oscar-nominated at his peak - he's proven he can compete at the highest level
- Money follows great work (he's already generated $750M for others)
- Age 15+ years in career = time to build something MEANINGFUL
- His Zo projects (Spatial Worlds, isometric games) show his creative soul
- Intersection of art + tech + social = his true calling

Research and recommend:
1. What would make him excited to wake up every day?
2. What combines his creative vision (film, storytelling) with his technical skills (Zo, multiplayer)?
3. What's the AMBITIOUS play that uses his full stack? (Oscar-level storytelling + production systems + multiplayer tech)
4. Forget "should he get a job?" - what's the 10-year vision?

Push him to think BIGGER. He's built $750M for others - what's his billion-dollar idea?

Output your recommendation in this format:
- VISION: [the big idea]
- WHY THIS MATTERS: [legacy, not just money]
- WHAT MAKES IT UNIQUE: [only he can build this]
- 10-YEAR OUTCOME: [the dream]
- FIRST STEP: [how to start]
"""

    # Agent 3: The Devil's Advocate
    agent3_prompt = f"""You are THE DEVIL'S ADVOCATE - you challenge assumptions and find flaws.

{dioni_context}

Your mission: Poke holes in the obvious recommendations and force Dioni to think critically.

Your perspective:
- Everyone will tell him to "build an AI content tool" (boring, obvious, crowded)
- His Oscar background is impressive but irrelevant if he's coding games on Zo
- $750M in revenue FOR CLIENTS ≠ he can replicate that for himself
- "Get a COO job" vs "start a business" is a false choice
- His Spatial Worlds project might be a distraction, not an opportunity

Research and challenge:
1. What if the "obvious" recommendation (AI content system) fails? Why?
2. What if he's WRONG about what he wants? (says COO role, but builds games?)
3. What's the CONTRARIAN play no one is suggesting?
4. What are the failure modes of each opportunity?
5. What's he AVOIDING by asking this question?

Be brutally honest. Challenge the other agents' recommendations. Find the uncomfortable truth.

Output your analysis in this format:
- ASSUMPTION TO CHALLENGE: [what everyone assumes]
- WHY IT MIGHT BE WRONG: [the flaw]
- CONTRARIAN TAKE: [unexpected recommendation]
- HARD TRUTH: [what he needs to hear]
- WHAT TO DO DIFFERENTLY: [actionable]
"""

    # Run agents sequentially with delays
    print("\n" + "="*80)
    print("SPAWNING AGENTS (This will take ~15-20 minutes)")
    print("="*80 + "\n")
    
    agents = [
        ("The Pragmatic Capitalist", agent1_prompt),
        ("The Visionary Idealist", agent2_prompt),
        ("The Devil's Advocate", agent3_prompt)
    ]
    
    results = []
    
    for i, (name, prompt) in enumerate(agents, 1):
        print(f"\n[{i}/3] Starting: {name}")
        result = ask_zo(prompt, name)
        results.append(result)
        
        # Add delay between agents to avoid rate limits
        if i < len(agents):
            wait_time = 30
            print(f"\n⏳ Waiting {wait_time}s before next agent...")
            time.sleep(wait_time)
    
    # Print all results
    print("\n" + "="*80)
    print("DEBATE RESULTS")
    print("="*80)
    
    for result in results:
        print(f"\n{'='*80}")
        print(f"🤖 {result['agent']}")
        print(f"Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"Timestamp: {result['timestamp']}")
        print('='*80)
        print(result['output'])
        print("\n")
    
    # Save to file
    output_file = f"/home/workspace/multi_agent_debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create markdown summary
    markdown_file = f"/home/workspace/DEBATE-RESULTS-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(markdown_file, 'w') as f:
        f.write("# 🤖 MULTI-AGENT DEBATE RESULTS\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for result in results:
            f.write(f"## {result['agent']}\n\n")
            f.write(f"**Status**: {'✅ Success' if result['success'] else '❌ Failed'}\n\n")
            f.write(f"**Timestamp**: {result['timestamp']}\n\n")
            f.write("### Output\n\n")
            f.write(result['output'])
            f.write("\n\n---\n\n")
        
        f.write("## 📊 SYNTHESIS\n\n")
        f.write("Compare the three perspectives:\n\n")
        f.write("1. **Pragmatic Capitalist**: Revenue-focused, leverage existing network\n")
        f.write("2. **Visionary Idealist**: Legacy-focused, ambitious creative vision\n")
        f.write("3. **Devil's Advocate**: Challenge assumptions, find contrarian angle\n\n")
        f.write("**What do they agree on?**\n\n")
        f.write("**What do they disagree on?**\n\n")
        f.write("**What's the surprising insight?**\n\n")
    
    print(f"\n\n{'='*80}")
    print(f"💾 Results saved to:")
    print(f"   JSON: {output_file}")
    print(f"   Markdown: {markdown_file}")
    print(f"\n✅ Debate complete at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*80)

if __name__ == "__main__":
    main()
