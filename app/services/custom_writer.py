"""
Custom Content Writer Module

This module provides flexible content generation capabilities using a multi-agent system.
It uses the same 5-agent orchestration as ai_blog_app but with customizable prompts
for different content types (summaries, reports, Q&A, analysis, etc.).

Agents:
1. Research Agent - Analyzes context and extracts key information
2. Content Planner - Creates structure and outline
3. Writer Agent - Generates main content
4. Reviewer Agent - Reviews and improves content
5. Editor Agent - Final polish and formatting
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import openai
import google.generativeai as genai

load_dotenv()

class WriterAgent:
    """
    Main writer agent that generates content based on topic, context, and content type.
    Copy your writer agent logic here and modify prompts based on content_type.
    """
    
    def __init__(self, model_client):
        self.model_client = model_client
    
    def get_writer_prompt(self, content_type: str, topic: str, context: str, max_words: int) -> str:
        """Get writer prompt based on content type"""
        
        base_context = f"""
Context from documents:
{context}

Topic: {topic}
Max words: {max_words}
"""
        
        prompts = {
            "summary": f"""
You are an expert content summarizer. Based on the provided context, create a comprehensive summary about the topic.

{base_context}

Instructions:
- Write a clear and concise summary
- Focus on the most important information related to the topic
- Use bullet points or structured format when appropriate
- Ensure accuracy based on the provided context
- Keep to approximately {max_words} words

Generate the summary:
""",
            
            "report": f"""
You are a professional report writer. Based on the provided context, create a detailed report about the topic.

{base_context}

Instructions:
- Create a structured report with clear sections
- Include an introduction, main findings, and conclusion
- Maintain a professional tone
- Support all statements with information from the context
- Keep to approximately {max_words} words

Generate the report:
""",
            
            "analysis": f"""
You are a data analyst. Based on the provided context, provide an analytical response about the topic.

{base_context}

Instructions:
- Analyze the information provided in the context
- Identify key patterns, trends, or insights
- Provide actionable conclusions
- Support your analysis with specific details from the context
- Keep to approximately {max_words} words

Generate the analysis:
""",
            
            "qa": f"""
You are a knowledgeable assistant. Based on the provided context, provide a comprehensive answer to the question.

{base_context}

Instructions:
- Answer the question directly and thoroughly
- Use information only from the provided context
- If the context doesn't contain enough information, state that clearly
- Be accurate and helpful
- Keep to approximately {max_words} words

Generate the answer:
"""
        }
        
        return prompts.get(content_type, prompts["summary"])
    
    async def generate_content(self, content_type: str, topic: str, context: str, max_words: int) -> str:
        """Generate content using the writer agent"""
        prompt = self.get_writer_prompt(content_type, topic, context, max_words)
        
        # TODO: Copy your writer generation logic here
        # return await self.model_client.generate(prompt)
        pass


class SEOReviewerAgent:
    """
    SEO Reviewer agent - focuses on search optimization and keyword usage.
    Copy your create_seo_reviewer logic here and adapt prompts for different content types.
    """
    
    def __init__(self, model_client):
        self.model_client = model_client
    
    def get_seo_review_prompt(self, content_type: str, content: str, topic: str) -> str:
        """Get SEO review prompt based on content type"""
        
        base_prompt = f"""
You are an SEO expert reviewer. Review the following {content_type} and improve it for search engine optimization.

Original {content_type}:
{content}

Topic: {topic}
"""
        
        if content_type == "summary":
            instructions = """
Instructions for SEO Summary Review:
- Ensure the topic/keywords appear naturally in the summary
- Add relevant keywords without keyword stuffing
- Make sure the summary is scannable and well-structured
- Optimize for featured snippets if applicable
"""
        elif content_type == "report":
            instructions = """
Instructions for SEO Report Review:
- Optimize headings and subheadings with relevant keywords
- Ensure proper structure for search engines
- Add relevant terms that users might search for
- Make the report easily scannable
"""
        elif content_type == "analysis":
            instructions = """
Instructions for SEO Analysis Review:
- Include industry-relevant keywords naturally
- Structure the analysis with clear headings
- Ensure the content answers common search queries
- Add context that helps with discoverability
"""
        else:  # qa
            instructions = """
Instructions for SEO Q&A Review:
- Optimize the answer for voice search queries
- Include related questions that users might ask
- Structure the answer clearly and concisely
- Use natural language that matches search intent
"""
        
        return base_prompt + instructions + "\n\nProvide the improved version:"
    
    async def review_content(self, content_type: str, content: str, topic: str) -> str:
        """Review content for SEO optimization"""
        prompt = self.get_seo_review_prompt(content_type, content, topic)
        
        # TODO: Copy your SEO reviewer generation logic here
        # return await self.model_client.generate(prompt)
        pass


class ContentMarketerReviewerAgent:
    """
    Content Marketing Reviewer agent - focuses on engagement and marketing effectiveness.
    Copy your create_content_marketer_reviewer logic here.
    """
    
    def __init__(self, model_client):
        self.model_client = model_client
    
    def get_marketing_review_prompt(self, content_type: str, content: str, topic: str) -> str:
        """Get content marketing review prompt based on content type"""
        
        base_prompt = f"""
You are a content marketing expert. Review the following {content_type} and improve it for better engagement and marketing effectiveness.

Current {content_type}:
{content}

Topic: {topic}
"""
        
        if content_type == "summary":
            instructions = """
Instructions for Marketing Summary Review:
- Make the summary more engaging and compelling
- Add hooks that grab attention
- Ensure it motivates readers to learn more
- Include calls-to-action where appropriate
"""
        elif content_type == "report":
            instructions = """
Instructions for Marketing Report Review:
- Make the report more engaging and reader-friendly
- Add compelling insights and takeaways
- Include actionable recommendations
- Ensure professional yet approachable tone
"""
        elif content_type == "analysis":
            instructions = """
Instructions for Marketing Analysis Review:
- Make the analysis more compelling and actionable
- Highlight key insights that drive decisions
- Use persuasive language while maintaining accuracy
- Add strategic recommendations
"""
        else:  # qa
            instructions = """
Instructions for Marketing Q&A Review:
- Make the answer more helpful and comprehensive
- Add value beyond just answering the question
- Include related insights or tips
- Ensure the tone is helpful and authoritative
"""
        
        return base_prompt + instructions + "\n\nProvide the improved version:"
    
    async def review_content(self, content_type: str, content: str, topic: str) -> str:
        """Review content for marketing effectiveness"""
        prompt = self.get_marketing_review_prompt(content_type, content, topic)
        
        # TODO: Copy your content marketing reviewer generation logic here
        # return await self.model_client.generate(prompt)
        pass


class ClarityAndEthicsReviewerAgent:
    """
    Clarity and Ethics Reviewer agent - focuses on clarity, accuracy, and ethical considerations.
    Copy your create_clarity_and_ethics_reviewer logic here.
    """
    
    def __init__(self, model_client):
        self.model_client = model_client
    
    def get_clarity_ethics_review_prompt(self, content_type: str, content: str, topic: str) -> str:
        """Get clarity and ethics review prompt based on content type"""
        
        base_prompt = f"""
You are a clarity and ethics expert. Review the following {content_type} for clarity, accuracy, and ethical considerations.

Current {content_type}:
{content}

Topic: {topic}
"""
        
        instructions = """
Instructions for Clarity and Ethics Review:
- Ensure all statements are clear and unambiguous
- Verify that claims are supported by the provided context
- Remove any potential bias or unfair representations
- Improve readability and comprehension
- Ensure ethical presentation of information
- Check for factual accuracy based on the source material
- Make sure the tone is appropriate and respectful
"""
        
        return base_prompt + instructions + "\n\nProvide the improved version:"
    
    async def review_content(self, content_type: str, content: str, topic: str) -> str:
        """Review content for clarity and ethics"""
        prompt = self.get_clarity_ethics_review_prompt(content_type, content, topic)
        
        # TODO: Copy your clarity and ethics reviewer generation logic here
        # return await self.model_client.generate(prompt)
        pass


# Main orchestration function
async def generate_custom_content_with_review(
    topic: str,
    context: str,
    content_type: str = "summary",
    provider: str = "openai",
    model: Optional[str] = None,
    max_words: int = 300
) -> str:
    """
    Generate content using the 4-agent system: Writer + 3 Reviewers
    
    Args:
        topic: The main topic or question
        context: Retrieved context from RAG pipeline
        content_type: Type of content (summary, report, analysis, qa)
        provider: LLM provider (openai, gemini)
        model: Specific model to use
        max_words: Maximum words in output
    
    Returns:
        Final reviewed and polished content
    """
    
    print(f"--- Starting custom content generation for: {topic} ---")
    print(f"--- Content type: {content_type} ---")
    
    try:
        # TODO: Initialize your model client here based on provider
        # model_client = YourModelClient(provider, model)
        model_client = None  # Placeholder
        
        # Initialize agents
        writer = WriterAgent(model_client)
        seo_reviewer = SEOReviewerAgent(model_client)
        marketing_reviewer = ContentMarketerReviewerAgent(model_client)
        clarity_reviewer = ClarityAndEthicsReviewerAgent(model_client)
        
        # Step 1: Generate initial content
        print("--- Step 1: Generating initial content ---")
        initial_content = await writer.generate_content(content_type, topic, context, max_words)
        
        # Step 2: SEO Review
        print("--- Step 2: SEO Review ---")
        seo_reviewed_content = await seo_reviewer.review_content(content_type, initial_content, topic)
        
        # Step 3: Content Marketing Review
        print("--- Step 3: Content Marketing Review ---")
        marketing_reviewed_content = await marketing_reviewer.review_content(content_type, seo_reviewed_content, topic)
        
        # Step 4: Clarity and Ethics Review
        print("--- Step 4: Clarity and Ethics Review ---")
        final_content = await clarity_reviewer.review_content(content_type, marketing_reviewed_content, topic)
        
        print("--- Custom content generation completed successfully ---")
        return final_content
        
    except Exception as e:
        print(f"--- ERROR during custom content generation: {repr(e)} ---")
        raise


# Convenience functions for different content types
async def generate_custom_summary(topic: str, context: str, provider: str = "openai", max_words: int = 300) -> str:
    """Generate a summary using the 4-agent review system"""
    return await generate_custom_content_with_review(topic, context, "summary", provider, max_words=max_words)

async def generate_custom_report(topic: str, context: str, provider: str = "openai", max_words: int = 500) -> str:
    """Generate a report using the 4-agent review system"""
    return await generate_custom_content_with_review(topic, context, "report", provider, max_words=max_words)

async def generate_custom_analysis(topic: str, context: str, provider: str = "openai", max_words: int = 400) -> str:
    """Generate an analysis using the 4-agent review system"""
    return await generate_custom_content_with_review(topic, context, "analysis", provider, max_words=max_words)

async def answer_custom_question(question: str, context: str, provider: str = "openai", max_words: int = 300) -> str:
    """Answer a question using the 4-agent review system"""
    return await generate_custom_content_with_review(question, context, "qa", provider, max_words=max_words)

class CustomContentWriter:
    """
    A flexible content writer that can generate various types of content
    using different LLM providers and custom prompts.
    """
    
    def __init__(self):
        # Initialize API clients
        self.openai_client = None
        self.gemini_model = None
        
        # Setup OpenAI if API key is available
        if os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = openai
        
        # Setup Gemini if API key is available
        if os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def generate_content(
        self,
        topic: str,
        context: str,
        content_type: str = "summary",
        provider: str = "openai",
        model: Optional[str] = None,
        max_words: int = 300,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Generate content based on the provided topic, context, and content type.
        
        Args:
            topic: The main topic or question
            context: Retrieved context from the RAG pipeline
            content_type: Type of content to generate (summary, report, qa, analysis)
            provider: LLM provider to use (openai, gemini)
            model: Specific model to use (optional)
            max_words: Maximum number of words in the response
            custom_prompt: Custom prompt template to use (optional)
        
        Returns:
            Generated content as a string
        """
        
        # Use custom prompt if provided, otherwise use predefined templates
        if custom_prompt:
            prompt = custom_prompt.format(topic=topic, context=context, max_words=max_words)
        else:
            prompt = self._get_prompt_template(content_type, topic, context, max_words)
        
        # Generate content based on provider
        if provider.lower() == "openai":
            return await self._generate_with_openai(prompt, model, max_words)
        elif provider.lower() == "gemini":
            return await self._generate_with_gemini(prompt, model, max_words)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_prompt_template(self, content_type: str, topic: str, context: str, max_words: int) -> str:
        """Get predefined prompt templates for different content types."""
        
        templates = {
            "summary": f"""
You are an expert content summarizer. Based on the following context, create a comprehensive summary about: {topic}

Context:
{context}

Instructions:
- Write a clear and concise summary in approximately {max_words} words
- Focus on the most important information related to the topic
- Use bullet points or structured format when appropriate
- Ensure accuracy based on the provided context

Summary:
""",
            
            "report": f"""
You are a professional report writer. Based on the following context, create a detailed report about: {topic}

Context:
{context}

Instructions:
- Create a structured report with clear sections
- Include an introduction, main findings, and conclusion
- Use approximately {max_words} words
- Maintain a professional tone
- Support all statements with information from the context

Report:
""",
            
            "qa": f"""
You are a knowledgeable assistant. Based on the following context, provide a comprehensive answer to this question: {topic}

Context:
{context}

Instructions:
- Answer the question directly and thoroughly
- Use information only from the provided context
- If the context doesn't contain enough information, state that clearly
- Keep your answer to approximately {max_words} words
- Be accurate and helpful

Answer:
""",
            
            "analysis": f"""
You are a data analyst. Based on the following context, provide an analytical response about: {topic}

Context:
{context}

Instructions:
- Analyze the information provided in the context
- Identify key patterns, trends, or insights
- Provide actionable conclusions
- Use approximately {max_words} words
- Support your analysis with specific details from the context

Analysis:
""",
            
            "comparison": f"""
You are a comparison expert. Based on the following context, create a comparison analysis for: {topic}

Context:
{context}

Instructions:
- Compare and contrast relevant elements from the context
- Highlight similarities and differences
- Use approximately {max_words} words
- Present information in a clear, structured format
- Base all comparisons on the provided context

Comparison:
"""
        }
        
        return templates.get(content_type, templates["summary"])
    
    async def _generate_with_openai(self, prompt: str, model: Optional[str], max_words: int) -> str:
        """Generate content using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        # Set default model if not specified
        if not model:
            model = "gpt-3.5-turbo"
        
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(max_words * 2, 4000),  # Rough token estimation
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _generate_with_gemini(self, prompt: str, model: Optional[str], max_words: int) -> str:
        """Generate content using Google Gemini."""
        if not self.gemini_model:
            raise ValueError("Gemini API key not configured")
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=min(max_words * 2, 8192),
                    temperature=0.7,
                )
            )
            
            return response.text.strip()
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

# Convenience functions for common use cases
async def generate_summary(topic: str, context: str, provider: str = "openai", max_words: int = 300) -> str:
    """Generate a summary based on the provided context."""
    writer = CustomContentWriter()
    return await writer.generate_content(topic, context, "summary", provider, max_words=max_words)

async def generate_report(topic: str, context: str, provider: str = "openai", max_words: int = 500) -> str:
    """Generate a detailed report based on the provided context."""
    writer = CustomContentWriter()
    return await writer.generate_content(topic, context, "report", provider, max_words=max_words)

async def answer_question(question: str, context: str, provider: str = "openai", max_words: int = 300) -> str:
    """Answer a question based on the provided context."""
    writer = CustomContentWriter()
    return await writer.generate_content(question, context, "qa", provider, max_words=max_words)

async def generate_analysis(topic: str, context: str, provider: str = "openai", max_words: int = 400) -> str:
    """Generate an analysis based on the provided context."""
    writer = CustomContentWriter()
    return await writer.generate_content(topic, context, "analysis", provider, max_words=max_words)