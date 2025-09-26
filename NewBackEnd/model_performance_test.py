#!/usr/bin/env python3
"""
Model Performance Test Script
Tests different Ollama models for quiz generation performance and quality.
"""

import ollama
import time
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPerformanceTester:
    def __init__(self):
        self.test_prompt = """Generate 3 quiz questions about Python programming based on this content:

Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.

Key features of Python include:
- Dynamic typing and automatic memory management
- Large standard library with many built-in modules
- Extensive third-party package ecosystem via PyPI
- Cross-platform compatibility
- Strong community support

Format each question as JSON:
{
    "type": "mcq",
    "question": "Question text here",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "A",
    "explanation": "Explanation here"
}

Return only the JSON array of questions."""

    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            models = ollama.list()
            return [model.get('name') for model in models.get('models', [])]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []

    def test_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Test a single model's performance."""
        logger.info(f"Testing model: {model_name}")
        
        try:
            # Test response time
            start_time = time.time()
            
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': self.test_prompt}],
                options={'timeout': 30}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Test response quality
            response_text = response['message']['content']
            
            # Try to parse JSON
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response_text[json_start:json_end]
                    questions = json.loads(json_str)
                    json_valid = True
                    question_count = len(questions)
                else:
                    json_valid = False
                    question_count = 0
                    
            except json.JSONDecodeError:
                json_valid = False
                question_count = 0
            
            return {
                'model': model_name,
                'response_time': round(response_time, 2),
                'json_valid': json_valid,
                'question_count': question_count,
                'response_length': len(response_text),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error testing {model_name}: {e}")
            return {
                'model': model_name,
                'response_time': 0,
                'json_valid': False,
                'question_count': 0,
                'response_length': 0,
                'success': False,
                'error': str(e)
            }

    def run_performance_test(self) -> List[Dict[str, Any]]:
        """Run performance test on all available models."""
        logger.info("Starting model performance test...")
        
        available_models = self.get_available_models()
        if not available_models:
            logger.error("No models available")
            return []
        
        logger.info(f"Found {len(available_models)} models: {available_models}")
        
        results = []
        for model in available_models:
            result = self.test_model_performance(model)
            results.append(result)
            logger.info(f"Completed test for {model}")
        
        return results

    def print_results(self, results: List[Dict[str, Any]]):
        """Print formatted test results."""
        print("\n" + "="*80)
        print("🎯 MODEL PERFORMANCE TEST RESULTS")
        print("="*80)
        
        # Sort by performance (response time + quality score)
        def performance_score(result):
            if not result['success']:
                return 999  # Worst score for failed models
            
            # Calculate quality score (0-100)
            quality_score = 0
            if result['json_valid']:
                quality_score += 50
            quality_score += min(result['question_count'] * 10, 30)  # Max 30 for questions
            quality_score += min(result['response_length'] / 100, 20)  # Max 20 for length
            
            # Lower response time is better, so subtract from 100
            time_score = max(0, 100 - (result['response_time'] * 10))
            
            return result['response_time'] - (quality_score / 100)  # Lower is better
        
        sorted_results = sorted(results, key=performance_score)
        
        print(f"{'Model':<20} {'Time(s)':<8} {'Valid':<6} {'Questions':<10} {'Length':<8} {'Score':<8}")
        print("-" * 80)
        
        for i, result in enumerate(sorted_results):
            if result['success']:
                quality_score = 0
                if result['json_valid']:
                    quality_score += 50
                quality_score += min(result['question_count'] * 10, 30)
                quality_score += min(result['response_length'] / 100, 20)
                
                print(f"{result['model']:<20} {result['response_time']:<8.2f} "
                      f"{'✓' if result['json_valid'] else '✗':<6} "
                      f"{result['question_count']:<10} "
                      f"{result['response_length']:<8} "
                      f"{quality_score:<8.0f}")
            else:
                print(f"{result['model']:<20} {'FAILED':<8} {'✗':<6} {'0':<10} {'0':<8} {'0':<8}")
        
        print("\n" + "="*80)
        print("🏆 RECOMMENDATIONS")
        print("="*80)
        
        # Get best performing models
        successful_models = [r for r in sorted_results if r['success']]
        
        if successful_models:
            best_model = successful_models[0]
            print(f"🥇 BEST OVERALL: {best_model['model']}")
            print(f"   • Response time: {best_model['response_time']:.2f}s")
            print(f"   • JSON valid: {'Yes' if best_model['json_valid'] else 'No'}")
            print(f"   • Questions generated: {best_model['question_count']}")
            
            # Find fastest model
            fastest_model = min(successful_models, key=lambda x: x['response_time'])
            if fastest_model != best_model:
                print(f"\n⚡ FASTEST: {fastest_model['model']} ({fastest_model['response_time']:.2f}s)")
            
            # Find best quality model
            quality_models = [r for r in successful_models if r['json_valid']]
            if quality_models:
                best_quality = max(quality_models, key=lambda x: x['question_count'])
                if best_quality != best_model:
                    print(f"\n🎯 BEST QUALITY: {best_quality['model']} ({best_quality['question_count']} questions)")
        else:
            print("❌ No models completed successfully")
        
        print("\n💡 TIPS FOR OPTIMAL PERFORMANCE:")
        print("   • Use llama3:latest for best overall performance")
        print("   • Use mistral:instruct as a reliable fallback")
        print("   • Set timeout to 30 seconds for quiz generation")
        print("   • Limit content length to 6000 characters for faster processing")
        print("   • Process questions in batches of 3-5 for better reliability")

def main():
    """Main function to run the performance test."""
    tester = ModelPerformanceTester()
    results = tester.run_performance_test()
    tester.print_results(results)

if __name__ == "__main__":
    main() 