from langgraph.graph import StateGraph, END
from langgraph.graph.message import MessageGraph
from langgraph.prebuilt import ToolNode
from typing import TypedDict, List, Dict, Any, Optional
from app.services.scanner import SecurityScanner
from app.services.rag_service import RAGRemediationService
from app.services.llm_service import LLMService

class SecurityState(TypedDict):
    code: str
    language: str
    filename: Optional[str]
    preferred_model: Optional[str]
    use_advanced_analysis: Optional[bool]
    scan_results: Dict[str, Any]
    vulnerabilities: List[Dict[str, Any]]
    remediation_suggestions: List[Dict[str, Any]]
    patches: List[Dict[str, Any]]
    assessments: List[Dict[str, Any]]
    classifications: List[Dict[str, Any]]  # New: fast classifications
    explanations: List[Dict[str, Any]]    # New: detailed explanations

class SecurityAgent:
    def __init__(self):
        self.scanner = SecurityScanner()
        self.rag = RAGRemediationService()
        self.llm_service = LLMService()  # Store as llm_service for access
        self.llm = self.llm_service  # Keep backward compatibility
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(SecurityState)

        # Define nodes
        workflow.add_node("scan", self._scan_node)
        workflow.add_node("extract_vulns", self._extract_vulns_node)
        workflow.add_node("retrieve_remediation", self._retrieve_remediation_node)
        workflow.add_node("generate_patches", self._generate_patches_node)
        workflow.add_node("assess_patches", self._assess_patches_node)
        workflow.add_node("advanced_analysis", self._advanced_analysis_node)  # New node

        # Define edges
        workflow.set_entry_point("scan")
        workflow.add_edge("scan", "extract_vulns")
        workflow.add_edge("extract_vulns", "retrieve_remediation")
        workflow.add_edge("retrieve_remediation", "generate_patches")
        workflow.add_edge("generate_patches", "assess_patches")
        workflow.add_edge("assess_patches", "advanced_analysis")
        workflow.add_edge("advanced_analysis", END)

        return workflow.compile()

    async def _scan_node(self, state: SecurityState) -> SecurityState:
        try:
            scan_results = await self.scanner.scan_code(
                state["code"], 
                state["language"],
                state.get("filename", "")
            )
            return {**state, "scan_results": scan_results}
        except Exception as e:
            return {**state, "scan_results": {"error": str(e)}}

    async def _extract_vulns_node(self, state: SecurityState) -> SecurityState:
        if "error" in state["scan_results"]:
            return {**state, "vulnerabilities": []}
        return {
            **state, 
            "vulnerabilities": state["scan_results"].get("vulnerabilities", [])
        }

    async def _retrieve_remediation_node(self, state: SecurityState) -> SecurityState:
        suggestions = []
        for vuln in state["vulnerabilities"]:
            try:
                recs = self.rag.retrieve_remediation(vuln)
                suggestions.append({"vuln": vuln, "recs": recs})
            except Exception as e:
                suggestions.append({
                    "vuln": vuln, 
                    "recs": [{"error": str(e)}]
                })
        return {**state, "remediation_suggestions": suggestions}

    async def _generate_patches_node(self, state: SecurityState) -> SecurityState:
        patches = []
        
        # Use preferred model if specified
        if state.get("preferred_model"):
            # Temporarily override the model for patch generation
            original_model = self.llm.patch_model
            self.llm.patch_model = state["preferred_model"]
        
        for suggestion in state["remediation_suggestions"]:
            for rec in suggestion["recs"]:
                try:
                    patch = await self.llm.generate_fix_diff(
                        suggestion["vuln"].get("code_snippet", ""),
                        suggestion["vuln"],
                        rec
                    )
                    patches.append({
                        "vuln": suggestion["vuln"],
                        "rec": rec,
                        "patch": patch
                    })
                except Exception as e:
                    patches.append({
                        "vuln": suggestion["vuln"],
                        "rec": rec,
                        "patch": {"error": str(e)}
                    })
        
        # Restore original model
        if state.get("preferred_model"):
            self.llm.patch_model = original_model
            
        return {**state, "patches": patches}

    async def _assess_patches_node(self, state: SecurityState) -> SecurityState:
        assessments = []
        for patch in state["patches"]:
            if "error" in patch["patch"]:
                assessments.append({
                    **patch,
                    "assessment": {"error": patch["patch"]["error"]}
                })
                continue
                
            try:
                assessment = await self.llm.assess_fix_quality(
                    patch["vuln"].get("code_snippet", ""),
                    patch["patch"].get("diff", ""),
                    patch["vuln"]
                )
                assessments.append({**patch, "assessment": assessment})
            except Exception as e:
                assessments.append({
                    **patch,
                    "assessment": {"error": str(e)}
                })
        return {**state, "assessments": assessments}

    async def _advanced_analysis_node(self, state: SecurityState) -> SecurityState:
        """New node for advanced multi-model analysis"""
        classifications = []
        explanations = []
        
        # Only run advanced analysis if requested
        if not state.get("use_advanced_analysis", False):
            return {
                **state, 
                "classifications": classifications,
                "explanations": explanations
            }
        
        # Fast vulnerability classification using Qwen
        for vuln in state["vulnerabilities"]:
            try:
                classification = await self.llm.classify_vulnerability_fast(
                    vuln.get("code_snippet", ""),
                    vuln
                )
                classifications.append({
                    "vuln": vuln,
                    "classification": classification
                })
            except Exception as e:
                classifications.append({
                    "vuln": vuln,
                    "classification": {"error": str(e)}
                })
        
        # Detailed security explanations using Kimi
        for vuln in state["vulnerabilities"]:
            try:
                explanation = await self.llm.explain_vulnerability(
                    vuln.get("code_snippet", ""),
                    vuln
                )
                explanations.append({
                    "vuln": vuln,
                    "explanation": explanation
                })
            except Exception as e:
                explanations.append({
                    "vuln": vuln,
                    "explanation": f"Error generating explanation: {str(e)}"
                })
        
        return {
            **state, 
            "classifications": classifications,
            "explanations": explanations
        }

    async def run(self, code: str, language: str, filename: str = "", 
                 preferred_model: str = None, use_advanced_analysis: bool = False) -> SecurityState:
        """
        Run security analysis with enhanced multi-model support
        
        Args:
            code: Code to analyze
            language: Programming language
            filename: Optional filename
            preferred_model: Optional preferred model for LLM operations
            use_advanced_analysis: Enable advanced multi-model features
        """
        init_state = SecurityState(
            code=code,
            language=language,
            filename=filename,
            preferred_model=preferred_model,
            use_advanced_analysis=use_advanced_analysis,
            scan_results={},
            vulnerabilities=[],
            remediation_suggestions=[],
            patches=[],
            assessments=[],
            classifications=[],
            explanations=[]
        )
        return await self.graph.ainvoke(init_state)
