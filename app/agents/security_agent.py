import asyncio
from typing import Dict, List, Any
from app.services.scanner import SecurityScanner
from app.services.rag_service import RAGRemediationService
from app.services.llm_service import LLMService

class SecurityAgent:
    def __init__(self):
        self.scanner = SecurityScanner()
        self.rag = RAGRemediationService()
        self.llm = LLMService()
    
    async def run(self, code: str, language: str) -> Dict[str, Any]:
        # Step 1: Scan code for vulnerabilities
        scan_results = await self.scanner.scan_code(code, language)
        
        if "error" in scan_results:
            return {"error": scan_results["error"]}
        
        # Step 2: Process vulnerabilities
        vulnerabilities = scan_results.get("vulnerabilities", [])
        remediation_suggestions = []
        patches = []
        assessments = []
        
        for vuln in vulnerabilities:
            # Step 3: Retrieve remediation patterns
            recs = self.rag.retrieve_remediation(vuln)
            remediation_suggestions.append({
                "vulnerability": vuln,
                "recommendations": recs
            })
            
            # Step 4: Generate fixes for each recommendation
            for rec in recs:
                patch = await self.llm.generate_fix_diff(
                    vuln.get("code_snippet", ""),
                    vuln,
                    rec
                )
                patches.append({
                    "vulnerability": vuln,
                    "recommendation": rec,
                    "patch": patch
                })
                
                # Step 5: Assess fix quality
                if "diff" in patch:
                    assessment = await self.llm.assess_fix_quality(
                        vuln.get("code_snippet", ""),
                        patch["diff"],
                        vuln
                    )
                    assessments.append(assessment)
        
        return {
            "scan_results": scan_results,
            "vulnerabilities": vulnerabilities,
            "remediation_suggestions": remediation_suggestions,
            "patches": patches,
            "assessments": assessments
        }