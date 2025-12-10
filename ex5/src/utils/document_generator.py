"""Document generation utilities for experiments.

This module provides realistic document generation for testing
LLM context window capabilities.
"""

import logging
import random
from typing import List, Optional, Dict, Any
from faker import Faker

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generator for realistic test documents.

    Creates documents with realistic structure and content
    for use in context window experiments.

    Attributes:
        fake: Faker instance for generating content
        random_seed: Random seed for reproducibility
    """

    def __init__(self, random_seed: Optional[int] = None):
        """Initialize document generator.

        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
            Faker.seed(random_seed)

        self.fake = Faker()
        logger.debug(f"Initialized DocumentGenerator with seed={random_seed}")

    def generate_filler_text(
        self,
        num_words: int = 200,
        style: str = "sentences"
    ) -> str:
        """Generate realistic filler text.

        Args:
            num_words: Target number of words
            style: Text style:
                - "sentences": Random sentences
                - "paragraphs": Random paragraphs
                - "lorem": Lorem ipsum text

        Returns:
            Generated text

        Example:
            >>> gen = DocumentGenerator(random_seed=42)
            >>> text = gen.generate_filler_text(100, style="sentences")
            >>> len(text.split()) >= 90  # Allow 10% variance
            True
        """
        if style == "sentences":
            # Generate sentences until we reach target word count
            text = []
            current_words = 0

            while current_words < num_words:
                sentence = self.fake.sentence()
                text.append(sentence)
                current_words += len(sentence.split())

            return " ".join(text)

        elif style == "paragraphs":
            # Generate paragraphs
            text = []
            current_words = 0
            sentences_per_para = 5

            while current_words < num_words:
                para = " ".join([
                    self.fake.sentence()
                    for _ in range(sentences_per_para)
                ])
                text.append(para)
                current_words += len(para.split())

            return "\n\n".join(text)

        elif style == "lorem":
            # Use lorem ipsum
            paragraphs = []
            current_words = 0

            while current_words < num_words:
                para = self.fake.paragraph(nb_sentences=5)
                paragraphs.append(para)
                current_words += len(para.split())

            return "\n\n".join(paragraphs)

        else:
            raise ValueError(f"Unknown style: {style}")

    def embed_critical_fact(
        self,
        text: str,
        fact: str,
        position: str = "middle"
    ) -> str:
        """Embed a critical fact at a specific position in text.

        Args:
            text: Base text to embed fact into
            fact: Critical fact to embed
            position: Position to embed fact:
                - "start": 0-10% into document
                - "middle": 45-55% into document
                - "end": 90-100% into document

        Returns:
            Text with embedded fact

        Example:
            >>> gen = DocumentGenerator(random_seed=42)
            >>> text = "word " * 100
            >>> result = gen.embed_critical_fact(text, "FACT", "middle")
            >>> "FACT" in result
            True
        """
        words = text.split()
        total_words = len(words)

        if total_words == 0:
            logger.warning("Empty text provided for fact embedding")
            return fact

        # Determine insertion position
        if position == "start":
            insert_idx = int(total_words * 0.05)  # 5% into document
        elif position == "middle":
            insert_idx = int(total_words * 0.50)  # Exactly middle
        elif position == "end":
            insert_idx = int(total_words * 0.95)  # 95% into document
        else:
            raise ValueError(f"Unknown position: {position}")

        # Insert fact with surrounding context
        words.insert(insert_idx, f" {fact} ")

        result = " ".join(words)
        logger.debug(
            f"Embedded fact at position={position} "
            f"(index {insert_idx}/{total_words})"
        )

        return result

    def generate_realistic_documents(
        self,
        num_docs: int = 20,
        words_per_doc: int = 200,
        topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate realistic documents across multiple topics.

        Args:
            num_docs: Number of documents to generate
            words_per_doc: Target words per document
            topics: List of topics (default: ["technology", "law", "medicine"])

        Returns:
            List of document dictionaries with metadata

        Example:
            >>> gen = DocumentGenerator(random_seed=42)
            >>> docs = gen.generate_realistic_documents(5, words_per_doc=100)
            >>> len(docs)
            5
            >>> "content" in docs[0] and "domain" in docs[0]
            True
        """
        if topics is None:
            topics = ["technology", "law", "medicine"]

        # Templates for different domains
        templates = {
            "technology": [
                "The {product} system developed by {company} uses {technology} "
                "to enable {capability}. Key features include {feature1} and {feature2}. "
                "Performance benchmarks show {metric} improvement over previous versions. "
                "The architecture is based on {architecture} principles. "
                "Future releases will focus on {future_feature}.",

                "Recent advances in {field} have led to the development of {technology}. "
                "This innovation allows {capability} with {metric} efficiency. "
                "{company} has been a leader in this space, releasing {product} "
                "which incorporates {feature1} and {feature2}.",
            ],
            "law": [
                "According to {law_name} enacted in {year}, {requirement}. "
                "Violations may result in {penalty}. The regulation applies to {scope}. "
                "Key provisions include {provision1} and {provision2}. "
                "Compliance requires {compliance_action}.",

                "The legal framework governing {domain} includes {law_name}. "
                "This statute establishes {requirement} for all entities operating in {scope}. "
                "Penalties for non-compliance include {penalty}. "
                "Recent case law has clarified that {clarification}.",
            ],
            "medicine": [
                "The medication {drug_name} is prescribed for treating {condition}. "
                "The recommended dosage is {dosage}. Common side effects include {side_effect1} "
                "and {side_effect2}. Contraindications include {contraindication}. "
                "Clinical trials have shown {efficacy} effectiveness.",

                "Medical procedure {procedure_name} is used to treat {condition}. "
                "The procedure involves {step1} followed by {step2}. "
                "Risks include {risk1} and {risk2}. Recovery time is typically {recovery}. "
                "Success rates are approximately {success_rate}.",
            ]
        }

        documents = []

        for i in range(num_docs):
            topic = random.choice(topics)
            template = random.choice(templates[topic])

            # Fill template with realistic data
            content = template.format(
                # Technology placeholders
                product=self.fake.word().capitalize() + " " + random.choice(["Pro", "X", "Suite"]),
                company=self.fake.company(),
                technology=random.choice(["AI", "blockchain", "cloud computing", "ML"]),
                capability=self.fake.bs(),
                feature1=self.fake.catch_phrase(),
                feature2=self.fake.catch_phrase(),
                metric=random.choice(["30%", "2x", "50%", "10x"]),
                architecture=random.choice(["microservices", "monolithic", "serverless"]),
                future_feature=self.fake.bs(),
                field=random.choice(["AI", "quantum computing", "robotics"]),

                # Law placeholders
                law_name=f"Act {random.randint(100, 999)} of {random.randint(2000, 2025)}",
                year=random.randint(2000, 2025),
                requirement=self.fake.sentence(),
                penalty=random.choice(["fines up to $10,000", "imprisonment", "suspension of license"]),
                scope=random.choice(["all businesses", "healthcare providers", "financial institutions"]),
                provision1=self.fake.sentence(),
                provision2=self.fake.sentence(),
                compliance_action=self.fake.sentence(),
                domain=random.choice(["privacy", "securities", "healthcare"]),
                clarification=self.fake.sentence(),

                # Medicine placeholders
                drug_name=self.fake.word().capitalize() + random.choice(["x", "ol", "in", "ex"]),
                condition=random.choice(["hypertension", "diabetes", "arthritis", "depression"]),
                dosage=f"{random.randint(50, 500)}mg {random.choice(['daily', 'twice daily', 'as needed'])}",
                side_effect1=random.choice(["nausea", "headache", "dizziness"]),
                side_effect2=random.choice(["fatigue", "dry mouth", "insomnia"]),
                contraindication=random.choice(["pregnancy", "liver disease", "kidney disease"]),
                efficacy=random.choice(["85%", "70%", "90%"]),
                procedure_name=random.choice(["arthroscopy", "angioplasty", "biopsy"]),
                step1=self.fake.sentence(),
                step2=self.fake.sentence(),
                risk1=random.choice(["infection", "bleeding", "scarring"]),
                risk2=random.choice(["pain", "swelling", "numbness"]),
                recovery=random.choice(["2-4 weeks", "1-2 months", "3-6 months"]),
                success_rate=random.choice(["85%", "90%", "95%"]),
            )

            # Pad to reach target word count
            current_words = len(content.split())
            if current_words < words_per_doc:
                filler = self.generate_filler_text(
                    words_per_doc - current_words,
                    style="sentences"
                )
                content = content + " " + filler

            # Create document dictionary
            doc = {
                "doc_id": f"doc_{i:03d}",
                "content": content,
                "domain": topic,
                "word_count": len(content.split()),
                "has_critical_fact": False,
                "critical_fact": None,
                "fact_position": None,
                "metadata": {
                    "generated_at": self.fake.iso8601(),
                    "template_id": topics.index(topic)
                }
            }

            documents.append(doc)

        logger.info(f"Generated {len(documents)} realistic documents")
        return documents

    def create_needle_haystack_document(
        self,
        haystack_words: int = 1000,
        needle: str = "The secret code is 7482",
        position: str = "middle"
    ) -> Dict[str, Any]:
        """Create a needle-in-haystack test document.

        Args:
            haystack_words: Size of haystack (filler text)
            needle: The critical fact to find
            position: Where to place the needle

        Returns:
            Document dictionary with embedded needle

        Example:
            >>> gen = DocumentGenerator(random_seed=42)
            >>> doc = gen.create_needle_haystack_document(
            ...     haystack_words=500,
            ...     needle="SECRET",
            ...     position="middle"
            ... )
            >>> "SECRET" in doc["content"]
            True
        """
        # Generate haystack
        haystack = self.generate_filler_text(
            haystack_words,
            style="sentences"
        )

        # Embed needle
        content = self.embed_critical_fact(haystack, needle, position)

        return {
            "content": content,
            "haystack_words": haystack_words,
            "needle": needle,
            "position": position,
            "total_words": len(content.split())
        }
