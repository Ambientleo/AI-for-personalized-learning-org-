#!/usr/bin/env python3
"""
Test script to verify enhanced quiz generator with different topics
"""
import requests
import json

def test_enhanced_quiz():
    base_url = "http://localhost:5004"
    
    print("🧪 Testing Enhanced Quiz Generator")
    print("=" * 50)
    
    # Test cases with different topics
    test_cases = [
        {
            "name": "React Quiz",
            "topic": "react",
            "expected_keywords": ["React", "JSX", "component", "hook"]
        },
        {
            "name": "JavaScript Quiz", 
            "topic": "javascript",
            "expected_keywords": ["JavaScript", "array", "const", "coercion"]
        },
        {
            "name": "Python Quiz",
            "topic": "python", 
            "expected_keywords": ["Python", "def", "list", "indentation"]
        },
        {
            "name": "Java Quiz",
            "topic": "java",
            "expected_keywords": ["Java", "main", "extends", "object-oriented"]
        },
        {
            "name": "HTML Quiz",
            "topic": "html",
            "expected_keywords": ["HTML", "markup", "tag", "DOCTYPE"]
        },
        {
            "name": "CSS Quiz",
            "topic": "css",
            "expected_keywords": ["CSS", "stylesheet", "color", "selector"]
        },
        {
            "name": "SQL Quiz",
            "topic": "sql",
            "expected_keywords": ["SQL", "database", "SELECT", "WHERE"]
        },
        {
            "name": "Machine Learning Quiz",
            "topic": "machine learning",
            "expected_keywords": ["learning", "supervised", "classification", "neural"]
        },
        {
            "name": "Data Science Quiz",
            "topic": "data science",
            "expected_keywords": ["data", "analysis", "pandas", "preprocessing"]
        },
        {
            "name": "General Programming Quiz",
            "topic": "programming",
            "expected_keywords": ["Python", "function", "programming"]
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Topic: {test_case['topic']}")
        
        try:
            payload = {
                "type": "topic",
                "content": test_case['topic'],
                "num_questions": 3,
                "question_types": ["mcq", "fill_blank", "true_false"]
            }
            
            response = requests.post(f"{base_url}/api/generate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                questions = data['questions']
                
                print(f"   ✅ Generated {len(questions)} questions")
                
                # Check if questions are relevant to the topic
                relevant_count = 0
                for question in questions:
                    question_text = question['question'].lower()
                    explanation = question['explanation'].lower()
                    
                    # Check if any expected keywords are in the question or explanation
                    for keyword in test_case['expected_keywords']:
                        if keyword.lower() in question_text or keyword.lower() in explanation:
                            relevant_count += 1
                            break
                
                relevance_percentage = (relevant_count / len(questions)) * 100
                print(f"   📊 Relevance: {relevance_percentage:.1f}% ({relevant_count}/{len(questions)} questions)")
                
                if relevance_percentage >= 50:
                    print(f"   ✅ Topic relevance is good")
                else:
                    print(f"   ⚠️  Topic relevance could be improved")
                    all_passed = False
                
                # Show sample question
                if questions:
                    sample_q = questions[0]
                    print(f"   📋 Sample: {sample_q['question'][:60]}...")
                
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Enhanced Quiz Generator is working excellently!")
        print("✅ All topics are generating relevant questions")
    else:
        print("⚠️  Enhanced Quiz Generator needs some improvements")
        print("❌ Some topics may not be generating relevant questions")
    
    print("\n📋 Summary of Supported Topics:")
    print("   • React, JavaScript, Python, Java")
    print("   • HTML, CSS, SQL")
    print("   • Machine Learning, Data Science")
    print("   • General Programming (falls back to Python)")
    
    print("\n🚀 The quiz generator now supports:")
    print("   ✅ Topic-specific question generation")
    print("   ✅ Smart topic matching and fallbacks")
    print("   ✅ Multiple question types (MCQ, Fill in blank, True/False)")
    print("   ✅ Customizable number of questions")
    print("   ✅ Relevant explanations for each answer")
    
    return all_passed

if __name__ == "__main__":
    test_enhanced_quiz() 