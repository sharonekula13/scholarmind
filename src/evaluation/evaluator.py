import json
import os


class RAGEvaluator:
    def __init__(self, retriever):
        self.retriever = retriever
        self.test_cases = []

    def add_test_case(self, question, expected_page, expected_keywords):
        self.test_cases.append({
            "question": question,
            "expected_page": expected_page,
            "expected_keywords": expected_keywords
        })

    def load_test_cases(self, file_path):
        with open(file_path, "r") as f:
            self.test_cases = json.load(f)

    def save_test_cases(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(self.test_cases, f, indent=2)

    def evaluate_retrieval(self, top_k=5):
        results = {
            "total_cases": len(self.test_cases),
            "recall_at_k": 0,
            "mrr": 0,
            "keyword_hit_rate": 0,
            "details": []
        }

        recall_hits = 0
        mrr_sum = 0
        keyword_hits = 0

        for case in self.test_cases:
            search_results = self.retriever.search(case["question"], top_k=top_k)

            # Check if expected page appears in results
            retrieved_pages = [r["page_number"] for r in search_results]
            page_found = case["expected_page"] in retrieved_pages

            if page_found:
                recall_hits += 1
                rank = retrieved_pages.index(case["expected_page"]) + 1
                mrr_sum += 1.0 / rank
            else:
                rank = -1

            # Check if expected keywords appear in retrieved text
            all_retrieved_text = " ".join([r["text"].lower() for r in search_results])
            keywords_found = []
            keywords_missing = []
            for keyword in case["expected_keywords"]:
                if keyword.lower() in all_retrieved_text:
                    keywords_found.append(keyword)
                else:
                    keywords_missing.append(keyword)

            keyword_score = len(keywords_found) / len(case["expected_keywords"]) if case["expected_keywords"] else 0
            keyword_hits += keyword_score

            results["details"].append({
                "question": case["question"],
                "expected_page": case["expected_page"],
                "page_found": page_found,
                "rank": rank,
                "keywords_found": keywords_found,
                "keywords_missing": keywords_missing,
                "keyword_score": keyword_score
            })

        results["recall_at_k"] = recall_hits / len(self.test_cases) if self.test_cases else 0
        results["mrr"] = mrr_sum / len(self.test_cases) if self.test_cases else 0
        results["keyword_hit_rate"] = keyword_hits / len(self.test_cases) if self.test_cases else 0

        return results

    def print_report(self, results):
        print("=" * 60)
        print("SCHOLARMIND RETRIEVAL EVALUATION REPORT")
        print("=" * 60)
        print(f"Total test cases: {results['total_cases']}")
        print(f"Recall@K:         {results['recall_at_k']:.2%}")
        print(f"MRR:              {results['mrr']:.2%}")
        print(f"Keyword Hit Rate: {results['keyword_hit_rate']:.2%}")
        print("=" * 60)
        print("\nDetailed Results:")
        for i, detail in enumerate(results["details"]):
            status = "✅" if detail["page_found"] else "❌"
            print(f"\n{status} Q{i+1}: {detail['question']}")
            print(f"   Expected page: {detail['expected_page']} | Found: {detail['page_found']} | Rank: {detail['rank']}")
            if detail["keywords_missing"]:
                print(f"   Missing keywords: {detail['keywords_missing']}")