"""Workflow manager for orchestrating trading workflows"""

import asyncio
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    
    name: str
    action: Callable
    retry_on_failure: bool = False
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    
    async def execute(self) -> Dict:
        """Execute workflow step
        
        Returns:
            Step result
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                if self.timeout_seconds:
                    result = await asyncio.wait_for(
                        self.action(),
                        timeout=self.timeout_seconds
                    )
                else:
                    result = await self.action()
                
                logger.info(f"Step '{self.name}' completed successfully")
                return {
                    "status": "success",
                    "result": result,
                    "retries": retry_count
                }
            except asyncio.TimeoutError:
                last_error = "Step timeout"
                logger.error(f"Step '{self.name}' timed out")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Step '{self.name}' failed: {e}")
            
            if self.retry_on_failure and retry_count < self.max_retries:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                logger.info(f"Retrying step '{self.name}' in {wait_time}s (attempt {retry_count})")
                await asyncio.sleep(wait_time)
            else:
                break
        
        return {
            "status": "failed",
            "error": last_error,
            "retries": retry_count
        }


class WorkflowManager:
    """Manages trading workflows"""
    
    def __init__(self):
        """Initialize workflow manager"""
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.workflow_history: List[Dict] = []
    
    def register_workflow(
        self,
        workflow_name: str,
        steps: List[WorkflowStep]
    ) -> None:
        """Register a new workflow
        
        Args:
            workflow_name: Name of the workflow
            steps: List of workflow steps
        """
        self.workflows[workflow_name] = steps
        logger.info(f"Registered workflow: {workflow_name} ({len(steps)} steps)")
    
    async def execute_workflow(
        self,
        workflow_name: str,
        stop_on_failure: bool = True
    ) -> Dict:
        """Execute a registered workflow
        
        Args:
            workflow_name: Name of workflow to execute
            stop_on_failure: Stop execution if any step fails
        
        Returns:
            Workflow execution result
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        steps = self.workflows[workflow_name]
        start_time = datetime.utcnow()
        results = []
        
        logger.info(f"Starting workflow: {workflow_name}")
        
        try:
            for step in steps:
                logger.info(f"Executing step: {step.name}")
                result = await step.execute()
                results.append({
                    "step_name": step.name,
                    **result
                })
                
                if result["status"] == "failed" and stop_on_failure:
                    logger.warning(f"Workflow '{workflow_name}' stopped due to step failure")
                    break
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            workflow_result = {
                "workflow_name": workflow_name,
                "status": "COMPLETED",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "steps_executed": len(results),
                "results": results
            }
            
            self.workflow_history.append(workflow_result)
            logger.info(f"Workflow '{workflow_name}' completed in {duration:.2f}s")
            return workflow_result
        except Exception as e:
            logger.error(f"Workflow '{workflow_name}' execution failed: {e}")
            raise
    
    async def execute_parallel_workflows(
        self,
        workflow_names: List[str]
    ) -> List[Dict]:
        """Execute multiple workflows in parallel
        
        Args:
            workflow_names: List of workflow names to execute
        
        Returns:
            List of workflow results
        """
        tasks = [self.execute_workflow(name) for name in workflow_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    def get_workflow_history(self, workflow_name: Optional[str] = None) -> List[Dict]:
        """Get workflow execution history
        
        Args:
            workflow_name: Filter by workflow name (optional)
        
        Returns:
            List of workflow executions
        """
        if workflow_name:
            return [w for w in self.workflow_history if w["workflow_name"] == workflow_name]
        return self.workflow_history
    
    def get_workflow_stats(self, workflow_name: str) -> Dict:
        """Get statistics for a workflow
        
        Args:
            workflow_name: Name of workflow
        
        Returns:
            Workflow statistics
        """
        executions = self.get_workflow_history(workflow_name)
        
        if not executions:
            return {"error": f"No executions found for workflow '{workflow_name}'"}
        
        durations = [e["duration_seconds"] for e in executions]
        
        return {
            "workflow_name": workflow_name,
            "total_executions": len(executions),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "last_execution": executions[-1]["end_time"]
        }
