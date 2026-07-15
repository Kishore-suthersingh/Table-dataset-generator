"""
Web Context Enricher - Search internet for reference datasets
Enhances synthetic data generation with real-world knowledge
"""
from typing import Dict, Any, List, Optional
import requests
from dataclasses import dataclass
import pandas as pd
from pattern_learner import PatternProfile


@dataclass
class ReferenceDataset:
    """Information about a reference dataset found online."""
    source: str
    description: str
    url: str
    data: pd.DataFrame
    relevance_score: float


class WebContextEnricher:
    """
    Search the web for reference datasets to enrich pattern learning.
    
    Strategy:
    1. Analyze user's sample dataset to identify domain/topic
    2. Search for related datasets online
    3. Download and parse reference data
    4. Merge with user's sample to create enriched dataset
    5. Use enriched data for pattern learning
    """
    
    def __init__(self, sample_df: pd.DataFrame, column_types: Dict[str, str]):
        self.sample_df = sample_df
        self.column_types = column_types
        self.reference_datasets: List[ReferenceDataset] = []
        self.enriched_df: Optional[pd.DataFrame] = None
    
    def identify_domain(self) -> str:
        """
        Identify the domain/topic of the dataset.
        
        Uses column names and sample values to determine domain.
        Examples: "sports", "finance", "healthcare", "ecommerce"
        """
        # Analyze column names for domain keywords
        columns_str = ' '.join(self.sample_df.columns).lower()
        
        # Domain detection patterns
        domain_patterns = {
            'sports': ['team', 'player', 'score', 'match', 'league', 'points', 'wins', 'goals'],
            'finance': ['price', 'stock', 'ticker', 'volume', 'market', 'trading', 'bitcoin', 'crypto'],
            'healthcare': ['patient', 'doctor', 'diagnosis', 'treatment', 'medication', 'hospital'],
            'ecommerce': ['product', 'order', 'customer', 'cart', 'purchase', 'shipping'],
            'education': ['student', 'grade', 'course', 'teacher', 'exam', 'GPA'],
        }
        
        # Count matches for each domain
        domain_scores = {}
        for domain, keywords in domain_patterns.items():
            score = sum(1 for keyword in keywords if keyword in columns_str)
            domain_scores[domain] = score
        
        # Return domain with highest score
        if max(domain_scores.values()) > 0:
            detected_domain = max(domain_scores, key=domain_scores.get)
            print(f"  ✓ Detected domain: {detected_domain}")
            return detected_domain
        
        return "general"
    
    def search_reference_data(self, domain: str) -> List[ReferenceDataset]:
        """
        Search for relevant reference datasets online.
        
        Sources:
        - Public datasets (Kaggle, data.gov, etc.)
        - APIs (sports stats, financial data, etc.)
        - Web scraping (tables from websites)
        """
        print(f"[Web Enrichment] Searching for {domain} reference data...")
        
        # Domain-specific data sources
        reference_sources = {
            'sports': [
                {
                    'name': 'Premier League Stats',
                    'description': 'Current Premier League standings',
                    'url': 'https://www.example.com/premier-league',  # Placeholder
                    'type': 'scrape'
                }
            ],
            'finance': [
                {
                    'name': 'Stock Market Data',
                    'description': 'Historical stock prices',
                    'url': 'https://api.example.com/stocks',  # Placeholder
                    'type': 'api'
                }
            ],
        }
        
        # For MVP: Use preloaded sample reference data
        reference_data = self._get_builtin_reference_data(domain)
        
        if reference_data:
            self.reference_datasets.append(reference_data)
            print(f"  ✓ Found reference dataset: {reference_data.source}")
        
        return self.reference_datasets
    
    def _get_builtin_reference_data(self, domain: str) -> Optional[ReferenceDataset]:
        """
        Get built-in reference datasets (MVP version).
        
        In production, this would be replaced with actual web scraping/API calls.
        """
        reference_samples = {
            'sports': pd.DataFrame({
                'team_name': ['Manchester United', 'Liverpool', 'Chelsea', 'Arsenal', 'Man City',
                             'Tottenham', 'Newcastle', 'Brighton', 'Aston Villa', 'West Ham',
                             'Crystal Palace', 'Wolves', 'Everton', 'Fulham', 'Brentford',
                             'Nottingham Forest', 'Bournemouth', 'Luton Town', 'Burnley', 'Sheffield United'],
                'stadium': ['Old Trafford', 'Anfield', 'Stamford Bridge', 'Emirates', 'Etihad',
                           'Tottenham Hotspur Stadium', 'St James Park', 'Amex Stadium', 'Villa Park', 'London Stadium',
                           'Selhurst Park', 'Molineux', 'Goodison Park', 'Craven Cottage', 'Gtech Community Stadium',
                           'City Ground', 'Vitality Stadium', 'Kenilworth Road', 'Turf Moor', 'Bramall Lane'],
                'city': ['Manchester', 'Liverpool', 'London', 'London', 'Manchester',
                        'London', 'Newcastle', 'Brighton', 'Birmingham', 'London',
                        'London', 'Wolverhampton', 'Liverpool', 'London', 'Brentford',
                        'Nottingham', 'Bournemouth', 'Luton', 'Burnley', 'Sheffield']
            }),
            
            'finance': pd.DataFrame({
                'ticker': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT'],
                'company': ['Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.', 'Amazon.com Inc.', 'Tesla Inc.',
                           'Meta Platforms', 'NVIDIA Corp.', 'JPMorgan Chase', 'Visa Inc.', 'Walmart Inc.'],
                'sector': ['Technology', 'Technology', 'Technology', 'Consumer', 'Automotive',
                          'Technology', 'Technology', 'Finance', 'Finance', 'Retail']
            }),
            
            'ecommerce': pd.DataFrame({
                'product_category': ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports',
                                    'Toys', 'Beauty', 'Food', 'Automotive', 'Health'],
                'typical_price_range': ['$50-500', '$20-100', '$10-50', '$30-300', '$25-150',
                                       '$10-80', '$15-100', '$5-50', '$20-200', '$10-75']
            })
        }
        
        if domain in reference_samples:
            return ReferenceDataset(
                source=f"Built-in {domain.title()} Reference",
                description=f"Curated {domain} reference data",
                url="internal",
                data=reference_samples[domain],
                relevance_score=0.85
            )
        
        return None
    
    def merge_datasets(self) -> pd.DataFrame:
        """
        Merge user's sample dataset with reference datasets.
        
        Strategy:
        1. Identify common columns
        2. Expand categorical values from reference data
        3. Adjust numerical ranges based on reference data
        4. Combine into enriched dataset
        """
        print("[Web Enrichment] Merging datasets...")
        
        if not self.reference_datasets:
            print("  ! No reference datasets to merge")
            return self.sample_df
        
        enriched_df = self.sample_df.copy()
        
        for ref_dataset in self.reference_datasets:
            ref_df = ref_dataset.data
            
            # Find matching or related columns
            for col in enriched_df.columns:
                col_lower = col.lower()
                
                # Check if reference has similar column
                for ref_col in ref_df.columns:
                    if col_lower in ref_col.lower() or ref_col.lower() in col_lower:
                        # Categorical enrichment: expand value set
                        if self.column_types.get(col) == 'categorical':
                            original_values = set(enriched_df[col].dropna().unique())
                            reference_values = set(ref_df[ref_col].dropna().unique())
                            
                            # Add reference values not in original
                            new_values = reference_values - original_values
                            if new_values:
                                print(f"  ✓ Enriched '{col}' with {len(new_values)} new values from reference")
                                
                                # Add new rows with reference values
                                # (keeping other columns similar to existing data)
                                for new_val in list(new_values)[:10]:  # Limit to 10 new values
                                    new_row = enriched_df.iloc[0].copy()  # Template from first row
                                    new_row[col] = new_val
                                    enriched_df = pd.concat([enriched_df, pd.DataFrame([new_row])], ignore_index=True)
        
        self.enriched_df = enriched_df
        print(f"  ✓ Enriched dataset: {len(self.sample_df)} → {len(enriched_df)} rows")
        
        return enriched_df
    
    def enrich(self) -> pd.DataFrame:
        """
        Main enrichment pipeline.
        
        Returns enriched dataset ready for pattern learning.
        """
        print("\n" + "="*60)
        print("WEB ENRICHMENT PIPELINE")
        print("="*60)
        
        # Step 1: Identify domain
        domain = self.identify_domain()
        
        # Step 2: Search for reference data
        self.search_reference_data(domain)
        
        # Step 3: Merge datasets
        enriched_df = self.merge_datasets()
        
        print("="*60)
        print(f"Enrichment complete: {len(self.sample_df)} → {len(enriched_df)} rows")
        print("="*60 + "\n")
        
        return enriched_df


# Example usage
if __name__ == "__main__":
    # Sample Premier League data
    sample = pd.DataFrame({
        'team_name': ['Arsenal', 'Man City', 'Liverpool'],
        'position': [1, 2, 3],
        'points': [68, 65, 63]
    })
    
    column_types = {
        'team_name': 'categorical',
        'position': 'numeric',
        'points': 'numeric'
    }
    
    # Enrich with web data
    enricher = WebContextEnricher(sample, column_types)
    enriched = enricher.enrich()
    
    print("\nOriginal sample:")
    print(sample)
    
    print("\nEnriched dataset:")
    print(enriched.head(10))
