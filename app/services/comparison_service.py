"""
Comparison Service
Handles text comparison and analysis between multiple documents.
"""
from typing import List, Dict, Any, Optional


class ComparisonService:
    """Service for comparing multiple documents."""

    def __init__(self):
        pass

    def extract_key_themes(self, text: str, max_themes: int = 5) -> List[str]:
        """
        Extract key themes from text.

        Args:
            text: Document text
            max_themes: Maximum number of themes to extract

        Returns:
            List of key themes/topics
        """
        # Simple keyword extraction based on frequency
        # In production, would use NLP or LLM

        import re
        from collections import Counter

        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

        # Remove common stop words
        stop_words = {
            'that', 'this', 'with', 'from', 'have', 'been',
            'were', 'they', 'their', 'what', 'when', 'where',
            'which', 'while', 'about', 'would', 'could', 'should',
            'there', 'these', 'those', 'being', 'other', 'some',
            'such', 'into', 'over', 'after', 'before', 'between',
            'under', 'through', 'during', 'each', 'only', 'than'
        }

        filtered = [w for w in words if w not in stop_words]

        # Get most common
        counter = Counter(filtered)
        themes = [word for word, _ in counter.most_common(max_themes)]

        return themes

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        # Simple Jaccard similarity
        import re

        words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def find_common_passages(
        self,
        texts: List[str],
        min_length: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find passages that appear in multiple texts.

        Args:
            texts: List of document texts
            min_length: Minimum passage length in words

        Returns:
            List of common passages with occurrence info
        """
        # Extract n-grams from each text
        from collections import defaultdict

        def get_ngrams(text: str, n: int) -> List[str]:
            words = text.lower().split()
            return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]

        # Find common n-grams
        ngram_counts = defaultdict(lambda: {"count": 0, "docs": set()})

        for doc_idx, text in enumerate(texts):
            for n in range(min_length, min_length + 5):
                for ngram in get_ngrams(text, n):
                    ngram_counts[ngram]["count"] += 1
                    ngram_counts[ngram]["docs"].add(doc_idx)

        # Filter to those appearing in multiple docs
        common = [
            {
                "passage": ngram,
                "doc_count": len(info["docs"]),
                "docs": list(info["docs"])
            }
            for ngram, info in ngram_counts.items()
            if len(info["docs"]) > 1
        ]

        # Sort by number of documents containing the passage
        common.sort(key=lambda x: x["doc_count"], reverse=True)

        return common[:20]  # Return top 20

    def get_word_frequency_comparison(
        self,
        texts: Dict[str, str],
        top_n: int = 20
    ) -> Dict[str, Dict[str, int]]:
        """
        Compare word frequencies across documents.

        Args:
            texts: Dict mapping document names to text content
            top_n: Number of top words to include

        Returns:
            Dict mapping each document to its top word frequencies
        """
        import re
        from collections import Counter

        stop_words = {
            'the', 'and', 'for', 'that', 'this', 'with', 'from',
            'have', 'been', 'were', 'they', 'their', 'what',
            'when', 'where', 'which', 'while'
        }

        result = {}

        for doc_name, text in texts.items():
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            filtered = [w for w in words if w not in stop_words]
            counter = Counter(filtered)
            result[doc_name] = dict(counter.most_common(top_n))

        return result

    def generate_comparison_summary(
        self,
        doc_summaries: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate a structured comparison summary.

        Args:
            doc_summaries: Dict mapping document names to their summaries

        Returns:
            Structured comparison data
        """
        doc_names = list(doc_summaries.keys())

        # Calculate pairwise similarities
        similarities = {}
        for i, name1 in enumerate(doc_names):
            for name2 in doc_names[i+1:]:
                sim = self.calculate_similarity(
                    doc_summaries[name1],
                    doc_summaries[name2]
                )
                similarities[f"{name1} vs {name2}"] = round(sim, 3)

        # Extract themes from each
        themes = {
            name: self.extract_key_themes(text)
            for name, text in doc_summaries.items()
        }

        # Find shared themes
        all_themes = [set(t) for t in themes.values()]
        if all_themes:
            shared_themes = all_themes[0]
            for t in all_themes[1:]:
                shared_themes = shared_themes & t
        else:
            shared_themes = set()

        return {
            "documents": doc_names,
            "pairwise_similarities": similarities,
            "themes_per_document": themes,
            "shared_themes": list(shared_themes),
            "document_count": len(doc_names)
        }
