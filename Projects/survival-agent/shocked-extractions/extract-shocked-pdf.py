#!/usr/bin/env python3
"""
Shocked PDF Token Extractor
Extracts token addresses and metadata from Shocked Discord PDFs
"""

import re
import sys
import json
from datetime import datetime
from pathlib import Path

def extract_tokens_from_pdf(pdf_path):
    """Extract pump.fun addresses from PDF binary data"""
    
    # Read PDF as binary and extract text
    with open(pdf_path, 'rb') as f:
        raw_data = f.read()
    
    # Decode with error handling
    text = raw_data.decode('utf-8', errors='ignore')
    
    # Find all pump.fun addresses (44 chars ending in 'pump')
    pump_pattern = r'([A-HJ-NP-Za-km-z1-9]{40,44}pump)'
    matches = re.findall(pump_pattern, text)
    
    # Clean addresses (remove common PDF artifacts like 'Lore' prefix)
    cleaned = []
    for addr in matches:
        clean = addr.replace('Lore', '').replace('tho', '')
        if len(clean) == 44 and clean.endswith('pump'):
            cleaned.append(clean)
    
    # Deduplicate
    unique_addresses = list(set(cleaned))
    
    # Extract context for each address
    tokens = []
    for addr in unique_addresses:
        # Find in original text
        idx = text.find(addr)
        if idx == -1:
            idx = text.find('Lore' + addr)
        if idx == -1:
            idx = text.find('tho' + addr)
        
        if idx != -1:
            # Get surrounding context
            start = max(0, idx - 300)
            end = min(len(text), idx + 300)
            context = text[start:end]
            
            # Extract metadata
            symbol = extract_symbol(context)
            fdv = extract_fdv(context)
            gain = extract_gain(context)
            
            tokens.append({
                'address': addr,
                'symbol': symbol,
                'fdv': fdv,
                'gain': gain
            })
        else:
            tokens.append({
                'address': addr,
                'symbol': 'UNKNOWN',
                'fdv': 'N/A',
                'gain': 0
            })
    
    # Sort by gain (highest first)
    tokens.sort(key=lambda x: x['gain'], reverse=True)
    
    return tokens

def extract_symbol(context):
    """Extract token symbol from context"""
    # Try $ prefix
    match = re.search(r'\$([A-Z][A-Za-z0-9]+)', context)
    if match:
        return match.group(1)
    
    # Try caps word
    match = re.search(r'\b([A-Z][A-Z0-9]{2,15})\b', context)
    if match:
        return match.group(1)
    
    return 'UNKNOWN'

def extract_fdv(context):
    """Extract FDV from context"""
    match = re.search(r'FDV[:\s]*\$?([\d.]+[KMB]?)', context, re.IGNORECASE)
    return match.group(1) if match else 'N/A'

def extract_gain(context):
    """Extract gain percentage from context"""
    match = re.search(r'(\d+)%', context)
    if match:
        return int(match.group(1))
    return 0

def determine_priority(gain, fdv_str):
    """Determine token priority based on metrics"""
    if gain >= 200:
        return 'high'
    elif gain >= 50:
        return 'medium'
    else:
        return 'low'

def save_extraction(tokens, output_dir):
    """Save extraction to organized files"""
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save addresses only
    with open(output_dir / 'addresses-only.txt', 'w') as f:
        for token in tokens:
            f.write(f"{token['address']}\n")
    
    # Save with metadata
    with open(output_dir / 'tokens-with-info.txt', 'w') as f:
        for token in tokens:
            f.write(f"{token['address']}\t{token['symbol']}\t{token['fdv']}\t{token['gain']}%\n")
    
    # Save summary markdown
    with open(output_dir / 'extraction-summary.md', 'w') as f:
        f.write(f"# Shocked Extraction - {output_dir.name}\n\n")
        f.write(f"**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n")
        f.write(f"**Total Tokens:** {len(tokens)}\n\n")
        
        # Priority breakdown
        high = [t for t in tokens if determine_priority(t['gain'], t['fdv']) == 'high']
        medium = [t for t in tokens if determine_priority(t['gain'], t['fdv']) == 'medium']
        low = [t for t in tokens if determine_priority(t['gain'], t['fdv']) == 'low']
        
        f.write(f"## Priority Breakdown\n")
        f.write(f"- 🔥 High: {len(high)} tokens (200%+ gains)\n")
        f.write(f"- ⚡ Medium: {len(medium)} tokens (50-200% gains)\n")
        f.write(f"- 📊 Low: {len(low)} tokens (<50% gains)\n\n")
        
        # List all tokens
        if high:
            f.write("### 🔥 High Priority\n")
            for t in high:
                f.write(f"- **{t['symbol']}** ({t['address'][:8]}...) - FDV: {t['fdv']}, +{t['gain']}%\n")
            f.write("\n")
        
        if medium:
            f.write("### ⚡ Medium Priority\n")
            for t in medium:
                f.write(f"- **{t['symbol']}** ({t['address'][:8]}...) - FDV: {t['fdv']}, +{t['gain']}%\n")
            f.write("\n")
        
        if low:
            f.write("### 📊 Low Priority\n")
            for t in low:
                f.write(f"- **{t['symbol']}** ({t['address'][:8]}...) - FDV: {t['fdv']}, +{t['gain']}%\n")
    
    print(f"✅ Extraction saved to {output_dir}")
    print(f"📊 Found {len(tokens)} tokens:")
    print(f"   🔥 High: {len(high)}")
    print(f"   ⚡ Medium: {len(medium)}")
    print(f"   📊 Low: {len(low)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract-shocked-pdf.py <path-to-pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Create output directory with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = Path(__file__).parent / today
    
    print(f"🔍 Extracting tokens from {pdf_path}...")
    tokens = extract_tokens_from_pdf(pdf_path)
    
    save_extraction(tokens, output_dir)
    
    print(f"\n📁 Files created:")
    print(f"   - addresses-only.txt")
    print(f"   - tokens-with-info.txt")
    print(f"   - extraction-summary.md")
    
    print(f"\n💡 Next step: Add to watchlist with:")
    print(f"   python3 add-to-watchlist.py {today}")

if __name__ == '__main__':
    main()
