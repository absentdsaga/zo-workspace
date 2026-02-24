"""
SUB-AGENT COORDINATOR (Python)

Implements @legendaryy's principle #1:
"Heavy tasks (Twitter research, market scans) should run as sub-agents,
not in the main session. Your main lane stays clean and doesn't accumulate
750K token context bombs"

Uses Zo's /zo/ask API to parallelize heavy market analysis tasks.
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MarketSignal:
    """Condensed market signal from sub-agent"""
    market_id: str
    question: str
    category: str
    edge_score: float  # 0-100
    current_price: float
    recommended_side: str  # 'YES' or 'NO'
    confidence: int  # 0-100
    key_factors: List[str]
    expected_value: float  # EV calculation


@dataclass
class ScanResult:
    """Result from a sub-agent scan"""
    signals: List[MarketSignal]
    metadata: Dict[str, Any]


class SubAgentCoordinator:
    """Coordinates parallel market analysis via sub-agents"""

    def __init__(self):
        self.api_key = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
        if not self.api_key:
            raise ValueError('ZO_CLIENT_IDENTITY_TOKEN not found in environment')

        self.base_url = 'https://api.zo.computer'

    async def parallel_market_scan(
        self,
        categories: List[str],
        time_range: str = "30-40",
        limit_per_category: int = 10
    ) -> List[ScanResult]:
        """
        Run parallel market scans across categories

        Args:
            categories: List of market categories to scan
            time_range: Time range for historical analysis (e.g. "30-40")
            limit_per_category: Max markets to analyze per category

        Returns:
            List of ScanResult objects with condensed signals
        """
        print(f"🔄 Launching {len(categories)} parallel market scans...")
        start_time = asyncio.get_event_loop().time()

        tasks = [
            self._run_category_scan(cat, time_range, limit_per_category)
            for cat in categories
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful = [r for r in results if isinstance(r, ScanResult)]
        failed = len([r for r in results if isinstance(r, Exception)])

        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"✅ Completed {len(successful)}/{len(categories)} scans in {elapsed:.1f}s")

        if failed > 0:
            print(f"⚠️  {failed} scans failed")

        return successful

    async def _run_category_scan(
        self,
        category: str,
        time_range: str,
        limit: int
    ) -> ScanResult:
        """Run a single category scan via /zo/ask API"""
        prompt = self._build_scan_prompt(category, time_range, limit)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/zo/ask',
                    headers={
                        'authorization': self.api_key,
                        'content-type': 'application/json'
                    },
                    json={'input': prompt}
                ) as response:
                    if not response.ok:
                        raise Exception(f"API returned {response.status}")

                    data = await response.json()
                    output = data['output']

                    return self._parse_scan_output(output, category)

        except Exception as e:
            print(f"❌ Category scan failed for {category}: {e}")
            return ScanResult(signals=[], metadata={'error': str(e)})

    def _build_scan_prompt(
        self,
        category: str,
        time_range: str,
        limit: int
    ) -> str:
        """
        Build comprehensive, self-contained prompt for sub-agent

        CRITICAL: Sub-agents have NO context from parent conversation.
        Include ALL information needed for the task.
        """
        return f"""You are a Polymarket edge analyzer. Your task: Analyze {category} markets for statistical edges.

REQUIREMENTS:
1. Scan up to {limit} markets in category: {category}
2. Analyze historical resolution data in {time_range}% price range
3. Calculate edge scores based on:
   - Price calibration (actual vs implied odds)
   - Volume and liquidity
   - Time until resolution
   - Historical accuracy in this category
4. Only include markets with edge_score >= 40
5. Return results in this EXACT format:

MARKET_START
MarketID: <market_id>
Question: <question_text>
Category: {category}
EdgeScore: <0-100>
CurrentPrice: <0.0-1.0>
RecommendedSide: <YES|NO>
Confidence: <0-100>
KeyFactors: <factor1,factor2,factor3>
ExpectedValue: <calculated_ev>
MARKET_END

METADATA_START
MarketsScanned: <number>
PassedFilter: <number>
ExecutionTime: <ms>
METADATA_END

DATA SOURCES:
- Use Polymarket API for current markets
- Use historical calibration data from /home/workspace/Projects/polymarket-bot/calibration.json
- Focus on {time_range}% price range (historically most profitable)

CONSTRAINTS:
- Only return high-confidence edges (score >= 40)
- Be concise - no explanations, just data
- Calculate EV = (prob_win * payout) - (prob_loss * stake)

Start analyzing now."""

    def _parse_scan_output(self, output: str, category: str) -> ScanResult:
        """Parse sub-agent's text response into structured data"""
        import re

        signals = []
        metadata = {
            'category': category,
            'markets_scanned': 0,
            'passed_filter': 0,
            'execution_time': 0
        }

        # Extract markets using regex
        market_pattern = r'MARKET_START\s+(.*?)\s+MARKET_END'
        market_matches = re.finditer(market_pattern, output, re.DOTALL)

        for match in market_matches:
            market_data = match.group(1)
            signal = self._parse_market_data(market_data)
            if signal:
                signals.append(signal)

        # Extract metadata
        metadata_pattern = r'METADATA_START\s+(.*?)\s+METADATA_END'
        metadata_match = re.search(metadata_pattern, output, re.DOTALL)

        if metadata_match:
            metadata_str = metadata_match.group(1)
            metadata.update(self._parse_metadata(metadata_str))

        return ScanResult(signals=signals, metadata=metadata)

    def _parse_market_data(self, data: str) -> Optional[MarketSignal]:
        """Parse individual market data from text"""
        try:
            lines = [l.strip() for l in data.split('\n') if l.strip()]
            fields = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    fields[key.strip()] = value.strip()

            return MarketSignal(
                market_id=fields.get('MarketID', ''),
                question=fields.get('Question', ''),
                category=fields.get('Category', ''),
                edge_score=float(fields.get('EdgeScore', 0)),
                current_price=float(fields.get('CurrentPrice', 0)),
                recommended_side=fields.get('RecommendedSide', 'YES'),
                confidence=int(fields.get('Confidence', 0)),
                key_factors=fields.get('KeyFactors', '').split(','),
                expected_value=float(fields.get('ExpectedValue', 0))
            )
        except Exception as e:
            print(f"Failed to parse market data: {e}")
            return None

    def _parse_metadata(self, data: str) -> Dict[str, Any]:
        """Parse metadata from text"""
        metadata = {}
        lines = [l.strip() for l in data.split('\n') if l.strip()]

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Convert to appropriate type
                if key == 'MarketsScanned':
                    metadata['markets_scanned'] = int(value)
                elif key == 'PassedFilter':
                    metadata['passed_filter'] = int(value)
                elif key == 'ExecutionTime':
                    metadata['execution_time'] = int(value)

        return metadata

    async def quick_scan(
        self,
        limit: int = 20
    ) -> List[MarketSignal]:
        """
        Simplified scan for quick checks
        Returns top N markets across all categories
        """
        categories = ['politics', 'crypto', 'sports']

        results = await self.parallel_market_scan(
            categories=categories,
            time_range="30-40",
            limit_per_category=limit // len(categories)
        )

        # Combine all signals and sort by edge score
        all_signals = []
        for result in results:
            all_signals.extend(result.signals)

        all_signals.sort(key=lambda s: s.edge_score, reverse=True)
        return all_signals[:limit]


# Example usage
async def main():
    coordinator = SubAgentCoordinator()

    # Quick scan
    signals = await coordinator.quick_scan(limit=10)

    print(f"\n📊 Found {len(signals)} market opportunities:\n")
    for signal in signals:
        print(f"  {signal.question[:60]}...")
        print(f"  Edge: {signal.edge_score:.1f} | Side: {signal.recommended_side} | EV: {signal.expected_value:.2f}")
        print(f"  Factors: {', '.join(signal.key_factors[:3])}\n")


if __name__ == '__main__':
    asyncio.run(main())
