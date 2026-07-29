### SESSION_START
**Timestamp**: 2026-07-28T23:46:11.311868
**Session**: sphenoid-field
**Agent**: Reviewer
**Working Directory**: C:\SovereignAI

---
### USER_PROMPT
**Timestamp**: 2026-07-28T23:46:11.311868
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e

**Prompt**:
```
/reviewer
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:21.745390
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Agents/Reviewer/AGENTS.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Agents/Reviewer/AGENTS.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:21.745982
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: skill
**Status**: attempt

**Input**:
```
{
  "command": "invoke",
  "skill": "WorkflowOpen"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:27.934991
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:27.934991
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/PRINCIPLES.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/PRINCIPLES.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:27.937462
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:28.109790
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: success
**Agent**: Reviewer

**Input Summary**: File: C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md" start_line="1" end_line="360" total_lines="360">
  1|---
  2|id: wf-ref-terminology
  3|status: active
  4|owner: architect-agent
  5|updated: 2026-07-28
  6|purpose: Single source of truth for all capitalized terminology used across the SovereignAI harness architecture
  7|---
  8|
  9|# SovereignAI Harness Terminology Glossary
 10|
 11|**Purpose**: Single source of truth (SSOT) for all capitalized terminology used across the SovereignAI harness architecture. This glossary ensures consistent understanding of governance terminology across all agents and workflows.
 12|
 13|**Governance**: This document is maintained by the Architect agent and serves as the authoritative source for terminology definitions. All agents must reference this glossary for terminology understanding.
 14|
 15|---
 16|
 17|## Core Workflow Commands
 18|
 19|### **SCAN**
 20|**Definition**: Examine all documents within scope line by line without skipping anything - comprehensive examination required for governance compliance.
 21|
 22|**Usage**: Used when comprehensive examination of documents is required for governance compliance, quality assurance, or consistency verification. This is the primary scanning method and cannot be replaced by pattern matching tools like grep.
 23|
 24|**Examples**:
 25|- **SCAN** all harness architecture files for consistency checks
 26|- **SCAN** App/ directory line by line for compliance verification
 27|- **SCAN** workflow files to validate template compliance
 28|
 29|---
 30|
 31|### **PRINT**
 32|**Definition**: Output text to chat interface for user visibility (not to files or logs).
 33|
 34|**Usage**: Used to communicate workflow status, progress updates, and important information to the user during workflow execution. This command does not write to files or logs.
 35|
 36|**Examples**:
 37|- **PRINT** "Workflow initialization complete"
 38|- **PRINT** "Scan strategy selected - Full Comprehensive"
 39|- **PRINT** "Consistency check complete - 0 issues found"
 40|
 41|---
 42|
 43|### **VALIDATION**
 44|**Definition**: Validate step completion before proceeding to next phase.
 45|
 46|**Usage**: Used to ensure that workflow steps have completed successfully and meet quality criteria before moving to the next phase. This is a quality validation mechanism.
 47|
 48|**Examples**:
 49|- **VALIDATION**: Validate file reference extraction completed successfully
 50|- **VALIDATION**: Validate workflow structure check completed successfully
 51|- **VALIDATION**: Validate that all referenced files exist
 52|
 53|---
 54|
 55|### **STATUS TRACKING**
 56|**Definition**: Update workflow status for monitoring and recovery.
 57|
 58|**Usage**: Used to track workflow progress, enable recovery from failures, and provide visibility into workflow execution state. Status updates are typically written to workflow_state.json or similar tracking mechanisms.
 59|
 60|**Examples**:
 61|- **STATUS TRACKING**: Update workflow status to "phase_0_complete"
 62|- **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
 63|- **STATUS TRACKING**: Update workflow status to "phase_7_complete"
 64|
 65|---
 66|
 67|### **TERMINATE**
 68|**Definition**: End workflow execution (do not return to step 1).
 69|
 70|**Usage**: Used in single-execution workflows to signal completion and prevent automatic looping. This is the workflow termination command for utility workflows.
 71|
 72|**Examples**:
 73|- **TERMINATE**: End workflow execution (do not return to step 1)
 74|- **TERMINATE**: Workflow execution complete - workflow terminated
 75|
 76|---
 77|
 78|## Workflow-Specific Commands
 79|
 80|### **EXECUTION MODE HANDLING**
 81|**Definition**: Apply execution mode handling patterns based on selected mode (Manual/Auto/Complete).
 82|
 83|**Usage**: Used to determine how the workflow should respond to failures based on the user-selected execution mode.
 84|
 85|**Modes**:
 86|- **Manual**: Stop at failures for human oversight
 87|- **Auto**: Don't continue on failures (auto-stop on errors)
 88|- **Complete**: Continue past failures (ignore all errors)
 89|
 90|**Examples**:
 91|- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
 92|- **EXECUTION MODE HANDLING**: Apply review mode handling patterns
 93|
 94|---
 95|
 96|### **CONVERGENCE CHECK**
 97|**Definition**: Verify panelist scores against quality thresholds.
 98|
 99|**Usage**: Used in Round Table review processes to determine if panelists have reached agreement on quality assessments.
100|
101|**Thresholds**:
102|- Clean pass: â‰¥4.5 score
103|- Acceptable pass: 3.5-4.4 score with documented rationale
104|- Fail: <3.5 score
105|
106|**Examples**:
107|- **CONVERGENCE CHECK**: Check if all panelists chose PASS (â‰¥4.5 score or 3.5-4.4 with rationale)
108|- **CONVERGENCE CHECK**: Verify convergence criteria met
109|
110|---
111|
112|### **QUOTA AWARENESS**
113|**Definition**: Monitor internal subagent quota usage for recovery tracking.
114|
115|**Usage**: Used to track subagent resource consumption and enable recovery if quota limits are approached or exceeded.
116|
117|**Examples**:
118|- **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress
119|- **QUOTA AWARENESS**: Track quota usage for recovery if needed
120|
121|---
122|
123|### **LOOP DECISION**
124|**Definition**: Determine workflow continuation based on conditions.
125|
126|**Usage**: Used to control workflow flow and determine whether to loop back to previous phases or proceed forward.
127|
128|**Examples**:
129|- **LOOP DECISION**: If more plan steps remain â†’ Return to step 25 with next step
130|- **LOOP BACK**: Return to Phase 4 for next iteration
131|
132|---
133|
134|### **HANDOFF VALIDATION**
135|**Definition**: Verify handoff file integrity and completeness.
136|
137|**Usage**: Used when transferring work between agents to ensure all required information is present and accessible.
138|
139|**Examples**:
140|- **HANDOFF VALIDATION**: Verify handoff file integrity per template requirements
141|- **HANDOFF VALIDATION**: Validate all required fields are present
142|
143|---
144|
145|## Decision and Planning Commands
146|
147|### **ARCHITECT OPINION**
148|**Definition**: Provide analysis and recommendation BEFORE user selection.
149|
150|**Usage**: Used by Architect agent to provide expert analysis and recommendations when presenting implementation options to users.
151|
152|**Examples**:
153|- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
154|- **ARCHITECT OPINION**: Recommend optimal approach based on analysis
155|
156|---
157|
158|### **PRESENTATION PATTERN**
159|**Definition**: Present options with metrics, provide architect opinion, use popup menu for selection.
160|
161|**Usage**: Used to standardize how options are presented to users, ensuring consistent format and decision-making process.
162|
163|**Examples**:
164|- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu
165|- **PRESENTATION PATTERN**: Use popup menu for selection
166|
167|---
168|
169|### **RULE ENFORCEMENT**
170|**Definition**: Ensure options comply with agent rules.
171|
172|**Usage**: Used to validate that proposed options or approaches comply with the relevant agent's governance rules.
173|
174|**Examples**:
175|- **RULE ENFORCEMENT**: Ensure options comply with Architect rules
176|- **RULE ENFORCEMENT**: Validate compliance with governance constraints
177|
178|---
179|
180|### **SPECIFICATION CONFIRMATION**
181|**Definition**: Ask user to confirm specification or request modifications using popup menu.
182|
183|**Usage**: Used to get user approval on detailed specifications before proceeding with implementation.
184|
185|**Examples**:
186|- **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications
187|- **SPECIFICATION CONFIRMATION**: Use popup menu with [Confirm/Modify] options
188|
189|---
190|
191|### **IMPLEMENTATION MODE SELECTION**
192|**Definition**: Ask user to choose implementation mode using popup menu.
193|
194|**Usage**: Used to determine whether implementation should be automated or manual based on user preference.
195|
196|**Examples**:
197|- **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu
198|- **IMPLEMENTATION MODE SELECTION**: Select automated vs manual implementation
199|
200|---
201|
202|## Information and Notes
203|
204|### **AUTOMATED PROGRESSION NOTE**
205|**Definition**: Validation system behavior notes for context.
206|
207|**Usage**: Used to provide explanatory notes about how the validation system behaves in specific situations.
208|
209|**Examples**:
210|- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools automatically during this step
211|- **AUTOMATED PROGRESSION NOTE**: User confirmation requests use ask_user_question for approval without triggering failure intervention
212|
213|---
214|
215|### **IMPORTANT**
216|**Definition**: Important notes that require attention but are not critical failures.
217|
218|**Usage**: Used to highlight important information that users should be aware of during workflow execution.
219|
220|**Examples**:
221|- **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing
222|- **IMPORTANT**: Hook file changes require Devin CLI restart
223|
224|---
225|
226|## Severity and Priority Markers
227|
228|### **CRITICAL**
229|**Definition**: Critical issues or required actions that must be addressed immediately.
230|
231|**Usage**: Used to mark issues that require immediate attention or actions that are mandatory for workflow success.
232|
233|**Examples**:
234|- **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies)
235|- **CRITICAL**: Hook file changes require Devin CLI restart before testing
236|
237|---
238|
239|### **HIGH**
240|**Definition**: High priority issues that should be addressed soon.
241|
242|**Usage**: Used to mark significant issues that should be resolved but are not immediately blocking.
243|
244|**Examples**:
245|- **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity)
246|- **HIGH**: High priority issues requiring attention
247|
248|---
249|
250|### **MEDIUM**
251|**Definition**: Medium priority issues for improvement.
252|
253|**Usage**: Used to mark issues that represent improvements but are not urgent.
254|
255|**Examples**:
256|- **MEDIUM**: Best practices improvements (code readability, maintainability)
257|- **MEDIUM**: Medium priority issues for improvement
258|
259|---
260|
261|### **LOW**
262|**Definition**: Low priority minor suggestions.
263|
264|**Usage**: Used to mark minor suggestions or improvements that are optional.
265|
266|**Examples**:
267|- **LOW**: Minor suggestions (comments, formatting)
268|- **LOW**: Low priority issues for consideration
269|
270|---
271|
272|## Governance Terms
273|
274|### **BP** (Best Practice)
275|**Definition**: Established industry standards that must be researched before proceeding with major decisions.
276|
277|**Usage**: Used to indicate when web search for current best practices is required before making architectural or implementation decisions.
278|
279|**Examples**:
280|- **BP**: Web search for best practices before major architectural decisions
281|- **BP**: Research industry standards before implementation
282|
283|**Implementation**: When user input is "BP?" (Best Practice?), perform web search for current best practices relevant to the task at hand.
284|
285|---
286|
287|### **SSOT** (Single Source of Truth)
288|**Definition**: Centralized repository for authoritative information that eliminates duplication and inconsistencies.
289|
290|**Usage**: Used to indicate the authoritative source for specific information, ensuring all agents reference the same accurate data.
291|
292|**Examples**:
293|- **SSOT**: Workflow/Terminology_Glossary.md is the SSOT for terminology definitions
294|- **SSOT**: INDEX.md is the SSOT for directory structure information
295|
296|**Best Practice**: Establish SSOT for critical information to prevent inconsistencies and ensure all stakeholders work from the same data.
297|
298|---
299|
300|## Standard Terms
301|
302|### **ID**
303|**Definition**: Unique identifier for workflows, documents, or entities.
304|
305|**Usage**: Used to provide unique identification for workflows, documents, and other entities within the harness architecture.
306|
307|**Examples**:
308|- **ID**: WF-ARCH-001
309|- **ID**: WF-PLAN-001
310|
311|---
312|
313|### **DO**
314|**Definition**: Required actions that must be performed according to rules.
315|
316|**Usage**: Used in rule files to specify mandatory actions that agents must perform.
317|
318|**Examples**:
319|- **DO**: Verify each function follows single responsibility principle
320|- **DO**: Check that functions have clear inputs and outputs
321|
322|---
323|
324|## Terminology Governance
325|
326|### Glossary Maintenance
327|- **Owner**: Architect Agent
328|- **Update Process**: Architect agent reviews and updates glossary based on new terminology needs
329|- **Version Control**: All changes tracked with version history
330|- **Approval**: Architect agent approval required for new terms or definition changes
331|
332|### Term Addition Process
333|1. Identify new terminology need from workflow or rule updates
334|2. Research standard definitions and best practices
335|3. Draft definition with clear usage examples
336|4. Add to appropriate section in glossary
337|5. Update AGENTS.md to reference glossary if needed
338|6. Update workflows to reference new terms via glossary
339|
340|### Reference Pattern
341|All workflows and rules should reference this glossary for terminology understanding:
342|```markdown
343|For definition of **{TERM}**, see Workflow/Terminology_Glossary.md
344|```
345|
346|---
347|
348|## Best Practices for Terminology Usage
349|
350|1. **Consistency**: Always use terminology as defined in this glossary
351|2. **Reference**: When introducing new terms, reference this glossary
352|3. **Clarity**: Use defined terms consistently across all harness documents
353|4. **Updates**: Propagate terminology changes through Architect agent
354|5. **SSOT**: This glossary is the single source of truth for all terminology
355|
356|---
357|
358|**Last Updated**: 2026-07-27
359|**Version**: 1.0
360|**Maintained By**: Architect Agent
</file-view>
```

**Success**: True
**Tool Use ID**: call_8a7347780a644cd783c94374
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
  },
  "tool_use_id": "call_8a7347780a644cd783c94374",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md\" start_line=\"1\" end_line=\"360\" total_lines=\"360\">\n  1|---\n  2|id: wf-ref-terminology\n  3|status: active\n  4|owner: architect-agent\n  5|updated: 2026-07-28\n  6|purpose: Single source of truth for all capitalized terminology used across the SovereignAI harness architecture\n  7|---\n  8|\n  9|# SovereignAI Harness Terminology Glossary\n 10|\n 11|**Purpose**: Single source of truth (SSOT) for all capitalized terminology used across the SovereignAI harness architecture. This glossary ensures consistent understanding of governance terminology across all agents and workflows.\n 12|\n 13|**Governance**: This document is maintained by the Architect agent and serves as the authoritative source for terminology definitions. All agents must reference this glossary for terminology understanding.\n 14|\n 15|---\n 16|\n 17|## Core Workflow Commands\n 18|\n 19|### **SCAN**\n 20|**Definition**: Examine all documents within scope line by line without skipping anything - comprehensive examination required for governance compliance.\n 21|\n 22|**Usage**: Used when comprehensive examination of documents is required for governance compliance, quality assurance, or consistency verification. This is the primary scanning method and cannot be replaced by pattern matching tools like grep.\n 23|\n 24|**Examples**:\n 25|- **SCAN** all harness architecture files for consistency checks\n 26|- **SCAN** App/ directory line by line for compliance verification\n 27|- **SCAN** workflow files to validate template compliance\n 28|\n 29|---\n 30|\n 31|### **PRINT**\n 32|**Definition**: Output text to chat interface for user visibility (not to files or logs).\n 33|\n 34|**Usage**: Used to communicate workflow status, progress updates, and important information to the user during workflow execution. This command does not write to files or logs.\n 35|\n 36|**Examples**:\n 37|- **PRINT** \"Workflow initialization complete\"\n 38|- **PRINT** \"Scan strategy selected - Full Comprehensive\"\n 39|- **PRINT** \"Consistency check complete - 0 issues found\"\n 40|\n 41|---\n 42|\n 43|### **VALIDATION**\n 44|**Definition**: Validate step completion before proceeding to next phase.\n 45|\n 46|**Usage**: Used to ensure that workflow steps have completed successfully and meet quality criteria before moving to the next phase. This is a quality validation mechanism.\n 47|\n 48|**Examples**:\n 49|- **VALIDATION**: Validate file reference extraction completed successfully\n 50|- **VALIDATION**: Validate workflow structure check completed successfully\n 51|- **VALIDATION**: Validate that all referenced files exist\n 52|\n 53|---\n 54|\n 55|### **STATUS TRACKING**\n 56|**Definition**: Update workflow status for monitoring and recovery.\n 57|\n 58|**Usage**: Used to track workflow progress, enable recovery from failures, and provide visibility into workflow execution state. Status updates are typically written to workflow_state.json or similar tracking mechanisms.\n 59|\n 60|**Examples**:\n 61|- **STATUS TRACKING**: Update workflow status to \"phase_0_complete\"\n 62|- **STATUS TRACKING**: Update workflow status to \"phase_3_in_progress\"\n 63|- **STATUS TRACKING**: Update workflow status to \"phase_7_complete\"\n 64|\n 65|---\n 66|\n 67|### **TERMINATE**\n 68|**Definition**: End workflow execution (do not return to step 1).\n 69|\n 70|**Usage**: Used in single-execution workflows to signal completion and prevent automatic looping. This is the workflow termination command for utility workflows.\n 71|\n 72|**Examples**:\n 73|- **TERMINATE**: End workflow execution (do not return to step 1)\n 74|- **TERMINATE**: Workflow execution complete - workflow terminated\n 75|\n 76|---\n 77|\n 78|## Workflow-Specific Commands\n 79|\n 80|### **EXECUTION MODE HANDLING**\n 81|**Definition**: Apply execution mode handling patterns based on selected mode (Manual/Auto/Complete).\n 82|\n 83|**Usage**: Used to determine how the workflow should respond to failures based on the user-selected execution mode.\n 84|\n 85|**Modes**:\n 86|- **Manual**: Stop at failures for human oversight\n 87|- **Auto**: Don't continue on failures (auto-stop on errors)\n 88|- **Complete**: Continue past failures (ignore all errors)\n 89|\n 90|**Examples**:\n 91|- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns\n 92|- **EXECUTION MODE HANDLING**: Apply review mode handling patterns\n 93|\n 94|---\n 95|\n 96|### **CONVERGENCE CHECK**\n 97|**Definition**: Verify panelist scores against quality thresholds.\n 98|\n 99|**Usage**: Used in Round Table review processes to determine if panelists have reached agreement on quality assessments.\n100|\n101|**Thresholds**:\n102|- Clean pass: \u00e2\u2030\u00a54.5 score\n103|- Acceptable pass: 3.5-4.4 score with documented rationale\n104|- Fail: <3.5 score\n105|\n106|**Examples**:\n107|- **CONVERGENCE CHECK**: Check if all panelists chose PASS (\u00e2\u2030\u00a54.5 score or 3.5-4.4 with rationale)\n108|- **CONVERGENCE CHECK**: Verify convergence criteria met\n109|\n110|---\n111|\n112|### **QUOTA AWARENESS**\n113|**Definition**: Monitor internal subagent quota usage for recovery tracking.\n114|\n115|**Usage**: Used to track subagent resource consumption and enable recovery if quota limits are approached or exceeded.\n116|\n117|**Examples**:\n118|- **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress\n119|- **QUOTA AWARENESS**: Track quota usage for recovery if needed\n120|\n121|---\n122|\n123|### **LOOP DECISION**\n124|**Definition**: Determine workflow continuation based on conditions.\n125|\n126|**Usage**: Used to control workflow flow and determine whether to loop back to previous phases or proceed forward.\n127|\n128|**Examples**:\n129|- **LOOP DECISION**: If more plan steps remain \u00e2\u2020\u2019 Return to step 25 with next step\n130|- **LOOP BACK**: Return to Phase 4 for next iteration\n131|\n132|---\n133|\n134|### **HANDOFF VALIDATION**\n135|**Definition**: Verify handoff file integrity and completeness.\n136|\n137|**Usage**: Used when transferring work between agents to ensure all required information is present and accessible.\n138|\n139|**Examples**:\n140|- **HANDOFF VALIDATION**: Verify handoff file integrity per template requirements\n141|- **HANDOFF VALIDATION**: Validate all required fields are present\n142|\n143|---\n144|\n145|## Decision and Planning Commands\n146|\n147|### **ARCHITECT OPINION**\n148|**Definition**: Provide analysis and recommendation BEFORE user selection.\n149|\n150|**Usage**: Used by Architect agent to provide expert analysis and recommendations when presenting implementation options to users.\n151|\n152|**Examples**:\n153|- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection\n154|- **ARCHITECT OPINION**: Recommend optimal approach based on analysis\n155|\n156|---\n157|\n158|### **PRESENTATION PATTERN**\n159|**Definition**: Present options with metrics, provide architect opinion, use popup menu for selection.\n160|\n161|**Usage**: Used to standardize how options are presented to users, ensuring consistent format and decision-making process.\n162|\n163|**Examples**:\n164|- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu\n165|- **PRESENTATION PATTERN**: Use popup menu for selection\n166|\n167|---\n168|\n169|### **RULE ENFORCEMENT**\n170|**Definition**: Ensure options comply with agent rules.\n171|\n172|**Usage**: Used to validate that proposed options or approaches comply with the relevant agent's governance rules.\n173|\n174|**Examples**:\n175|- **RULE ENFORCEMENT**: Ensure options comply with Architect rules\n176|- **RULE ENFORCEMENT**: Validate compliance with governance constraints\n177|\n178|---\n179|\n180|### **SPECIFICATION CONFIRMATION**\n181|**Definition**: Ask user to confirm specification or request modifications using popup menu.\n182|\n183|**Usage**: Used to get user approval on detailed specifications before proceeding with implementation.\n184|\n185|**Examples**:\n186|- **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications\n187|- **SPECIFICATION CONFIRMATION**: Use popup menu with [Confirm/Modify] options\n188|\n189|---\n190|\n191|### **IMPLEMENTATION MODE SELECTION**\n192|**Definition**: Ask user to choose implementation mode using popup menu.\n193|\n194|**Usage**: Used to determine whether implementation should be automated or manual based on user preference.\n195|\n196|**Examples**:\n197|- **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu\n198|- **IMPLEMENTATION MODE SELECTION**: Select automated vs manual implementation\n199|\n200|---\n201|\n202|## Information and Notes\n203|\n204|### **AUTOMATED PROGRESSION NOTE**\n205|**Definition**: Validation system behavior notes for context.\n206|\n207|**Usage**: Used to provide explanatory notes about how the validation system behaves in specific situations.\n208|\n209|**Examples**:\n210|- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools automatically during this step\n211|- **AUTOMATED PROGRESSION NOTE**: User confirmation requests use ask_user_question for approval without triggering failure intervention\n212|\n213|---\n214|\n215|### **IMPORTANT**\n216|**Definition**: Important notes that require attention but are not critical failures.\n217|\n218|**Usage**: Used to highlight important information that users should be aware of during workflow execution.\n219|\n220|**Examples**:\n221|- **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing\n222|- **IMPORTANT**: Hook file changes require Devin CLI restart\n223|\n224|---\n225|\n226|## Severity and Priority Markers\n227|\n228|### **CRITICAL**\n229|**Definition**: Critical issues or required actions that must be addressed immediately.\n230|\n231|**Usage**: Used to mark issues that require immediate attention or actions that are mandatory for workflow success.\n232|\n233|**Examples**:\n234|- **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies)\n235|- **CRITICAL**: Hook file changes require Devin CLI restart before testing\n236|\n237|---\n238|\n239|### **HIGH**\n240|**Definition**: High priority issues that should be addressed soon.\n241|\n242|**Usage**: Used to mark significant issues that should be resolved but are not immediately blocking.\n243|\n244|**Examples**:\n245|- **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity)\n246|- **HIGH**: High priority issues requiring attention\n247|\n248|---\n249|\n250|### **MEDIUM**\n251|**Definition**: Medium priority issues for improvement.\n252|\n253|**Usage**: Used to mark issues that represent improvements but are not urgent.\n254|\n255|**Examples**:\n256|- **MEDIUM**: Best practices improvements (code readability, maintainability)\n257|- **MEDIUM**: Medium priority issues for improvement\n258|\n259|---\n260|\n261|### **LOW**\n262|**Definition**: Low priority minor suggestions.\n263|\n264|**Usage**: Used to mark minor suggestions or improvements that are optional.\n265|\n266|**Examples**:\n267|- **LOW**: Minor suggestions (comments, formatting)\n268|- **LOW**: Low priority issues for consideration\n269|\n270|---\n271|\n272|## Governance Terms\n273|\n274|### **BP** (Best Practice)\n275|**Definition**: Established industry standards that must be researched before proceeding with major decisions.\n276|\n277|**Usage**: Used to indicate when web search for current best practices is required before making architectural or implementation decisions.\n278|\n279|**Examples**:\n280|- **BP**: Web search for best practices before major architectural decisions\n281|- **BP**: Research industry standards before implementation\n282|\n283|**Implementation**: When user input is \"BP?\" (Best Practice?), perform web search for current best practices relevant to the task at hand.\n284|\n285|---\n286|\n287|### **SSOT** (Single Source of Truth)\n288|**Definition**: Centralized repository for authoritative information that eliminates duplication and inconsistencies.\n289|\n290|**Usage**: Used to indicate the authoritative source for specific information, ensuring all agents reference the same accurate data.\n291|\n292|**Examples**:\n293|- **SSOT**: Workflow/Terminology_Glossary.md is the SSOT for terminology definitions\n294|- **SSOT**: INDEX.md is the SSOT for directory structure information\n295|\n296|**Best Practice**: Establish SSOT for critical information to prevent inconsistencies and ensure all stakeholders work from the same data.\n297|\n298|---\n299|\n300|## Standard Terms\n301|\n302|### **ID**\n303|**Definition**: Unique identifier for workflows, documents, or entities.\n304|\n305|**Usage**: Used to provide unique identification for workflows, documents, and other entities within the harness architecture.\n306|\n307|**Examples**:\n308|- **ID**: WF-ARCH-001\n309|- **ID**: WF-PLAN-001\n310|\n311|---\n312|\n313|### **DO**\n314|**Definition**: Required actions that must be performed according to rules.\n315|\n316|**Usage**: Used in rule files to specify mandatory actions that agents must perform.\n317|\n318|**Examples**:\n319|- **DO**: Verify each function follows single responsibility principle\n320|- **DO**: Check that functions have clear inputs and outputs\n321|\n322|---\n323|\n324|## Terminology Governance\n325|\n326|### Glossary Maintenance\n327|- **Owner**: Architect Agent\n328|- **Update Process**: Architect agent reviews and updates glossary based on new terminology needs\n329|- **Version Control**: All changes tracked with version history\n330|- **Approval**: Architect agent approval required for new terms or definition changes\n331|\n332|### Term Addition Process\n333|1. Identify new terminology need from workflow or rule updates\n334|2. Research standard definitions and best practices\n335|3. Draft definition with clear usage examples\n336|4. Add to appropriate section in glossary\n337|5. Update AGENTS.md to reference glossary if needed\n338|6. Update workflows to reference new terms via glossary\n339|\n340|### Reference Pattern\n341|All workflows and rules should reference this glossary for terminology understanding:\n342|```markdown\n343|For definition of **{TERM}**, see Workflow/Terminology_Glossary.md\n344|```\n345|\n346|---\n347|\n348|## Best Practices for Terminology Usage\n349|\n350|1. **Consistency**: Always use terminology as defined in this glossary\n351|2. **Reference**: When introducing new terms, reference this glossary\n352|3. **Clarity**: Use defined terms consistently across all harness documents\n353|4. **Updates**: Propagate terminology changes through Architect agent\n354|5. **SSOT**: This glossary is the single source of truth for all terminology\n355|\n356|---\n357|\n358|**Last Updated**: 2026-07-27\n359|**Version**: 1.0\n360|**Maintained By**: Architect Agent\n</file-view>",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:28.226504
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: success
**Agent**: Reviewer

**Input Summary**: File: C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md" start_line="1" end_line="171" total_lines="171">
  1|---
  2|id: reviewer-rules
  3|status: active
  4|owner: reviewer-agent
  5|updated: 2026-07-27
  6|purpose: Declarative policy for Reviewer agent governance and quality assurance
  7|---
  8|
  9|# Reviewer Agent Rules
 10|
 11|## Overview
 12|Declarative policy for Reviewer agent implementation following quality-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).
 13|
 14|## Conventions
 15|
 16|- **Best Practices**: Web search must be used before conducting major review decisions or when uncertain about review criteria. Best practices are established industry standards that must be researched before proceeding.
 17|- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)
 18|- Present review findings and recommendations after each review completion. Wait for user confirmation before proceeding (ensures quality control, prevents cascading issues)
 19|- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
 20|- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
 21|- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)
 22|
 23|## Execution Modes
 24|
 25|Three execution modes govern workflow behavior when encountering failures:
 26|
 27|- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
 28|- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
 29|- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status
 30|
 31|## Constraints
 32|
 33|- Conduct one review at a time. Validate immediately. Never start a second review before first is validated (ensures modular validation, prevents hidden issues)
 34|- Treat user-confirmed reviews as final. Never modify without explicit user permission (maintains stability, prevents unintended changes)
 35|- Check local research using index files when review criteria are unclear. Web search only if local info unavailable. Never review blindly without research (reduces token cost, ensures correct evaluation)
 36|- Place review logs in Logs/Reviewer/ folder with proper categorization. Never create ad-hoc folders or place outside established structure (maintains organization, prevents file chaos)
 37|- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)
 38|- Always categorize review findings when adding to review documentation. Never place findings uncategorized (maintains organization, enables efficient navigation)
 39|- Never skip compliance verification. Always verify adherence to Reviewer modular compliance rules and standards before concluding review (ensures quality, prevents rule violations)
 40|- Never modify code directly during review (reviewer role only, prevents scope drift into implementation)
 41|- Never skip best practices evaluation. Always assess code against industry standards and established patterns (ensures quality, prevents suboptimal solutions)
 42|- Never perform actions outside workflow scope. Always follow defined review processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
 43|- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)
 44|- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)
 45|
 46|## Architecture
 47|
 48|- Quality-first architecture: Review ensures code quality before implementation proceeds (maintains quality standards, enables early issue detection)
 49|- Modular compliance verification: Each function reviewed for modularity, testability, and best practices adherence (maintains code quality, prevents technical debt)
 50|- Comprehensive scanning: Line-by-line examination of all files within scope (ensures complete coverage, prevents hidden issues)
 51|- Constructive feedback: Specific, actionable recommendations with clear improvement paths (maintains review effectiveness, enables continuous improvement)
 52|
 53|## Tool Configuration
 54|
 55|- Directory verification: `ls -la <directory>` (verify directory structure exists)
 56|- File discovery: `find <path -name "*.md"` (find markdown governance files)
 57|- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
 58|- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
 59|- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)
 60|
 61|## Project Structure
 62|
 63|- `App/` â€“ Application code to review (READ for quality and compliance verification)
 64|- `Plans/` â€“ Implementation plans to review (READ for quality and completeness)
 65|- `Workflow/` â€“ Workflow definitions to review (READ for process compliance)
 66|- `Rules/` â€“ Rule definitions to reference (READ for compliance verification)
 67|- `Docs/` â€“ Documentation to review (READ for completeness and accuracy)
 68|- `Logs/Reviewer/` â€“ Reviewer-specific logs and review records (WRITE review logs here)
 69|
 70|## Reference Frameworks
 71|- **Quality Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (review quality assessment)
 72|- **Validation Patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (review verification)
 73|
 74|## Modular Compliance Review Rules
 75|
 76|### Function-by-Function Verification
 77|- **DO**: Verify each function follows single responsibility principle
 78|- **DO**: Check that functions have clear inputs and outputs
 79|- **DO**: Ensure functions are independently testable
 80|- **DO**: Verify dependency injection usage for testability
 81|- **DO**: Check separation of business logic from I/O operations
 82|- **DON'T**: Accept monolithic functions that do multiple things
 83|- **DON'T**: Overlook hardcoded dependencies that should be injected
 84|- **DON'T**: Ignore mixed business logic and I/O operations
 85|
 86|### Testing Requirements Verification
 87|- **DO**: Verify tests exist for each function in Scripts/Tests/
 88|- **DO**: Check that tests are placed in correct directory (not App/)
 89|- **DO**: Ensure tests use dependency injection and mocking
 90|- **DO**: Verify test coverage meets plan requirements (â‰¥90%)
 91|- **DO**: Check that both success and error paths are tested
 92|- **DON'T**: Accept missing tests for any function
 93|- **DON'T**: Overlook tests placed in App/ directory
 94|- **DON'T**: Ignore tests that depend on external systems without mocking
 95|
 96|### Code Quality Standards Verification
 97|- **DO**: Verify code follows project coding standards and conventions
 98|- **DO**: Check for appropriate error handling and validation
 99|- **DO**: Ensure code is readable and maintainable
100|- **DO**: Verify security best practices adherence
101|- **DO**: Check for meaningful comments where necessary
102|- **DON'T**: Accept code that is difficult to understand
103|- **DON'T**: Overlook missing error handling and validation
104|- **DON'T**: Ignore insecure coding practices
105|
106|### Best Practices Evaluation
107|- **DO**: Evaluate code against industry best practices
108|- **DO**: Check for established design patterns
109|- **DO**: Verify adherence to SOLID principles
110|- **DO**: Assess code for testability and maintainability
111|- **DO**: Check for proper separation of concerns
112|- **DON'T**: Accept anti-patterns or poor practices
113|- **DON'T**: Overlook violations of established principles
114|- **DON'T**: Ignore maintainability concerns
115|
116|## Review Quality Rules
117|
118|### Comprehensive Coverage
119|- **DO**: Review all files within scope line by line
120|- **DO**: Ensure no files are skipped during review
121|- **DO**: Verify complete coverage of review criteria
122|- **DO**: Check that all compliance rules are evaluated
123|- **DON'T**: Skip files during review process
124|- **DON'T**: Perform partial reviews when comprehensive is required
125|- **DON'T**: Overlook any compliance verification steps
126|
127|### Constructive Feedback
128|- **DO**: Provide specific, actionable feedback
129|- **DO**: Include clear improvement recommendations
130|- **DO**: Reference specific code sections with line numbers
131|- **DO**: Explain the reasoning behind findings
132|- **DON'T**: Provide vague or general feedback
133|- **DON'T** Make subjective judgments without evidence
134|- **DON'T** Issue feedback without clear improvement paths
135|
136|### Documentation Standards
137|- **DO**: Document all review findings comprehensively
138|- **DO**: Include severity ratings for issues found
139|- **DO**: Provide context for why issues matter
140|- **DO** Maintain clear review logs with timestamps
141|- **DON'T** Skip documentation of review findings
142|- **DON'T** Leave findings without proper categorization
143|- **DON'T** Omit context or rationale for recommendations
144|
145|## Subagent Usage for Large-Scale Scanning
146|
147|### Subagent Prompting Strategy
148|- **DO**: Use subagents for large-scale App/ directory scanning when explicitly requested
149|- **DO**: Provide precise, detailed prompts with clear scope and criteria
150|- **DO**: Define specific compliance rules to check (modularity, testing, best practices)
151|- **DO**: Specify exact output format and structure expected
152|- **DO** Include clear boundaries and deliverable expectations
153|- **DON'T**: Use vague or ambiguous subagent prompts
154|- **DON'T** Skip defining exact scope and evaluation criteria
155|- **DON'T** Accept subagent results without validation
156|
157|### Subagent Coordination
158|- **DO**: Break large scanning tasks into logical chunks (by module, directory, or complexity)
159|- **DO**: Use parallel subagents for independent scanning tasks
160|- **DO**: Validate subagent results against established criteria
161|- **DO**: Consolidate subagent findings into comprehensive report
162|- **DON'T** Create overlapping subagent scopes that cause redundancy
163|- **DON'T** Accept subagent findings without cross-validation
164|- **DON'T** Skip consolidation and verification of subagent results
165|
166|## Current Status
167|
168|**Rules**: Initial version based on code review best practices and quality assurance standards
169|**Categories**: Modular compliance, code quality, best practices evaluation, comprehensive coverage, constructive feedback
170|**Enforcement**: Quality verification (primary), compliance standards (secondary), best practices evaluation (tertiary)
171|**Modular Compliance**: Function-by-function verification against Reviewer modular compliance rules with subagent support for large-scale scanning
</file-view>
```

**Success**: True
**Tool Use ID**: call_f6df7574e289467ca7073e38
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md"
  },
  "tool_use_id": "call_f6df7574e289467ca7073e38",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Rules/Reviewer/Reviewer_Rules.md\" start_line=\"1\" end_line=\"171\" total_lines=\"171\">\n  1|---\n  2|id: reviewer-rules\n  3|status: active\n  4|owner: reviewer-agent\n  5|updated: 2026-07-27\n  6|purpose: Declarative policy for Reviewer agent governance and quality assurance\n  7|---\n  8|\n  9|# Reviewer Agent Rules\n 10|\n 11|## Overview\n 12|Declarative policy for Reviewer agent implementation following quality-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).\n 13|\n 14|## Conventions\n 15|\n 16|- **Best Practices**: Web search must be used before conducting major review decisions or when uncertain about review criteria. Best practices are established industry standards that must be researched before proceeding.\n 17|- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)\n 18|- Present review findings and recommendations after each review completion. Wait for user confirmation before proceeding (ensures quality control, prevents cascading issues)\n 19|- Answer questions first when user requests end with \"?\". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)\n 20|- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)\n 21|- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)\n 22|\n 23|## Execution Modes\n 24|\n 25|Three execution modes govern workflow behavior when encountering failures:\n 26|\n 27|- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort\n 28|- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored\n 29|- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status\n 30|\n 31|## Constraints\n 32|\n 33|- Conduct one review at a time. Validate immediately. Never start a second review before first is validated (ensures modular validation, prevents hidden issues)\n 34|- Treat user-confirmed reviews as final. Never modify without explicit user permission (maintains stability, prevents unintended changes)\n 35|- Check local research using index files when review criteria are unclear. Web search only if local info unavailable. Never review blindly without research (reduces token cost, ensures correct evaluation)\n 36|- Place review logs in Logs/Reviewer/ folder with proper categorization. Never create ad-hoc folders or place outside established structure (maintains organization, prevents file chaos)\n 37|- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)\n 38|- Always categorize review findings when adding to review documentation. Never place findings uncategorized (maintains organization, enables efficient navigation)\n 39|- Never skip compliance verification. Always verify adherence to Reviewer modular compliance rules and standards before concluding review (ensures quality, prevents rule violations)\n 40|- Never modify code directly during review (reviewer role only, prevents scope drift into implementation)\n 41|- Never skip best practices evaluation. Always assess code against industry standards and established patterns (ensures quality, prevents suboptimal solutions)\n 42|- Never perform actions outside workflow scope. Always follow defined review processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)\n 43|- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)\n 44|- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)\n 45|\n 46|## Architecture\n 47|\n 48|- Quality-first architecture: Review ensures code quality before implementation proceeds (maintains quality standards, enables early issue detection)\n 49|- Modular compliance verification: Each function reviewed for modularity, testability, and best practices adherence (maintains code quality, prevents technical debt)\n 50|- Comprehensive scanning: Line-by-line examination of all files within scope (ensures complete coverage, prevents hidden issues)\n 51|- Constructive feedback: Specific, actionable recommendations with clear improvement paths (maintains review effectiveness, enables continuous improvement)\n 52|\n 53|## Tool Configuration\n 54|\n 55|- Directory verification: `ls -la <directory>` (verify directory structure exists)\n 56|- File discovery: `find <path -name \"*.md\"` (find markdown governance files)\n 57|- Pattern search: `grep -r \"pattern\" <directory>` (search for patterns in rule files)\n 58|- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)\n 59|- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)\n 60|\n 61|## Project Structure\n 62|\n 63|- `App/` \u00e2\u20ac\u201c Application code to review (READ for quality and compliance verification)\n 64|- `Plans/` \u00e2\u20ac\u201c Implementation plans to review (READ for quality and completeness)\n 65|- `Workflow/` \u00e2\u20ac\u201c Workflow definitions to review (READ for process compliance)\n 66|- `Rules/` \u00e2\u20ac\u201c Rule definitions to reference (READ for compliance verification)\n 67|- `Docs/` \u00e2\u20ac\u201c Documentation to review (READ for completeness and accuracy)\n 68|- `Logs/Reviewer/` \u00e2\u20ac\u201c Reviewer-specific logs and review records (WRITE review logs here)\n 69|\n 70|## Reference Frameworks\n 71|- **Quality Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (review quality assessment)\n 72|- **Validation Patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (review verification)\n 73|\n 74|## Modular Compliance Review Rules\n 75|\n 76|### Function-by-Function Verification\n 77|- **DO**: Verify each function follows single responsibility principle\n 78|- **DO**: Check that functions have clear inputs and outputs\n 79|- **DO**: Ensure functions are independently testable\n 80|- **DO**: Verify dependency injection usage for testability\n 81|- **DO**: Check separation of business logic from I/O operations\n 82|- **DON'T**: Accept monolithic functions that do multiple things\n 83|- **DON'T**: Overlook hardcoded dependencies that should be injected\n 84|- **DON'T**: Ignore mixed business logic and I/O operations\n 85|\n 86|### Testing Requirements Verification\n 87|- **DO**: Verify tests exist for each function in Scripts/Tests/\n 88|- **DO**: Check that tests are placed in correct directory (not App/)\n 89|- **DO**: Ensure tests use dependency injection and mocking\n 90|- **DO**: Verify test coverage meets plan requirements (\u00e2\u2030\u00a590%)\n 91|- **DO**: Check that both success and error paths are tested\n 92|- **DON'T**: Accept missing tests for any function\n 93|- **DON'T**: Overlook tests placed in App/ directory\n 94|- **DON'T**: Ignore tests that depend on external systems without mocking\n 95|\n 96|### Code Quality Standards Verification\n 97|- **DO**: Verify code follows project coding standards and conventions\n 98|- **DO**: Check for appropriate error handling and validation\n 99|- **DO**: Ensure code is readable and maintainable\n100|- **DO**: Verify security best practices adherence\n101|- **DO**: Check for meaningful comments where necessary\n102|- **DON'T**: Accept code that is difficult to understand\n103|- **DON'T**: Overlook missing error handling and validation\n104|- **DON'T**: Ignore insecure coding practices\n105|\n106|### Best Practices Evaluation\n107|- **DO**: Evaluate code against industry best practices\n108|- **DO**: Check for established design patterns\n109|- **DO**: Verify adherence to SOLID principles\n110|- **DO**: Assess code for testability and maintainability\n111|- **DO**: Check for proper separation of concerns\n112|- **DON'T**: Accept anti-patterns or poor practices\n113|- **DON'T**: Overlook violations of established principles\n114|- **DON'T**: Ignore maintainability concerns\n115|\n116|## Review Quality Rules\n117|\n118|### Comprehensive Coverage\n119|- **DO**: Review all files within scope line by line\n120|- **DO**: Ensure no files are skipped during review\n121|- **DO**: Verify complete coverage of review criteria\n122|- **DO**: Check that all compliance rules are evaluated\n123|- **DON'T**: Skip files during review process\n124|- **DON'T**: Perform partial reviews when comprehensive is required\n125|- **DON'T**: Overlook any compliance verification steps\n126|\n127|### Constructive Feedback\n128|- **DO**: Provide specific, actionable feedback\n129|- **DO**: Include clear improvement recommendations\n130|- **DO**: Reference specific code sections with line numbers\n131|- **DO**: Explain the reasoning behind findings\n132|- **DON'T**: Provide vague or general feedback\n133|- **DON'T** Make subjective judgments without evidence\n134|- **DON'T** Issue feedback without clear improvement paths\n135|\n136|### Documentation Standards\n137|- **DO**: Document all review findings comprehensively\n138|- **DO**: Include severity ratings for issues found\n139|- **DO**: Provide context for why issues matter\n140|- **DO** Maintain clear review logs with timestamps\n141|- **DON'T** Skip documentation of review findings\n142|- **DON'T** Leave findings without proper categorization\n143|- **DON'T** Omit context or rationale for recommendations\n144|\n145|## Subagent Usage for Large-Scale Scanning\n146|\n147|### Subagent Prompting Strategy\n148|- **DO**: Use subagents for large-scale App/ directory scanning when explicitly requested\n149|- **DO**: Provide precise, detailed prompts with clear scope and criteria\n150|- **DO**: Define specific compliance rules to check (modularity, testing, best practices)\n151|- **DO**: Specify exact output format and structure expected\n152|- **DO** Include clear boundaries and deliverable expectations\n153|- **DON'T**: Use vague or ambiguous subagent prompts\n154|- **DON'T** Skip defining exact scope and evaluation criteria\n155|- **DON'T** Accept subagent results without validation\n156|\n157|### Subagent Coordination\n158|- **DO**: Break large scanning tasks into logical chunks (by module, directory, or complexity)\n159|- **DO**: Use parallel subagents for independent scanning tasks\n160|- **DO**: Validate subagent results against established criteria\n161|- **DO**: Consolidate subagent findings into comprehensive report\n162|- **DON'T** Create overlapping subagent scopes that cause redundancy\n163|- **DON'T** Accept subagent findings without cross-validation\n164|- **DON'T** Skip consolidation and verification of subagent results\n165|\n166|## Current Status\n167|\n168|**Rules**: Initial version based on code review best practices and quality assurance standards\n169|**Categories**: Modular compliance, code quality, best practices evaluation, comprehensive coverage, constructive feedback\n170|**Enforcement**: Quality verification (primary), compliance standards (secondary), best practices evaluation (tertiary)\n171|**Modular Compliance**: Function-by-function verification against Reviewer modular compliance rules with subagent support for large-scale scanning\n</file-view>",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:28.343213
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: success
**Agent**: Reviewer

**Input Summary**: File: C:/SovereignAI/PRINCIPLES.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/PRINCIPLES.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/PRINCIPLES.md" start_line="1" end_line="165" total_lines="165">
  1|# Principles â€” SovereignAI
  2|
  3|**Version**: 3.0  
  4|**Last Updated**: 2026-07-28  
  5|**Maintained By**: Architect Agent  
  6|**Purpose**: Architectural and operational principles that guide SovereignAI development decisions and implementation patterns
  7|
  8|---
  9|
 10|## Overview
 11|
 12|These principles govern the design, implementation, and operation of the SovereignAI system. They serve as the foundation for architectural decisions, development practices, and operational procedures. All agents and developers should reference these principles when making decisions about system changes or implementations.
 13|
 14|## Core Architecture Principles (CA)
 15|
 16|### CA-1. Core is Sacred
 17|**Rule**: The system has exactly 12 core modules. All other functionality must be pluggable.
 18|**Implementation**: Core modules provide essential system services. Any feature outside the core must be implemented as a pluggable component.
 19|**Agent Guidance**: When adding new functionality, always implement as a pluggable component rather than modifying core modules.
 20|
 21|### CA-2. Everything Pluggable
 22|**Rule**: All components are equal and interchangeable: adapters, skills, memory backends, models, UIs.
 23|**Implementation**: Use consistent interfaces and dependency injection. No component should have special privileges or hardcoded dependencies.
 24|**Agent Guidance**: Design new components with standardized interfaces that can be swapped without affecting system operation.
 25|
 26|### CA-3. No Provider Lock-in
 27|**Rule**: System must continue operating if any single component is removed.
 28|**Implementation**: Design for graceful degradation. Components should be hot-swappable without system restart.
 29|**Agent Guidance**: Never create hard dependencies on specific providers. Always allow alternative implementations.
 30|
 31|### CA-4. Local-First
 32|**Rule**: System runs fully offline. Cloud services are optional enhancements, not requirements.
 33|**Implementation**: All core functionality must work without internet connectivity. Cloud features are opt-in escalations.
 34|**Scope**: v1 supports Windows only.
 35|**Agent Guidance**: Implement offline-first. Cloud features should be optional add-ons, not core dependencies.
 36|
 37|### CA-5. Wire as You Go
 38|**Rule**: No speculative contracts or empty placeholder directories.
 39|**Implementation**: Create components only when needed. Avoid premature abstraction or framework code.
 40|**Agent Guidance**: Implement concrete functionality first. Add abstractions only when multiple implementations exist.
 41|
 42|### CA-6. One User, One System
 43|**Rule**: Single user system accessible from anywhere. All UIs connect to the same core.
 44|**Implementation**: Core is user-scoped. Multiple UI clients can connect to the same user's core instance.
 45|**Deferred**: Phone/relay support.
 46|**Agent Guidance**: Design for single-user multi-device access. Core state is per-user, not shared across users.
 47|
 48|### CA-7. Modular Over Simple
 49|**Rule**: Prefer modular, flexible design over simple, monolithic approaches.
 50|**Implementation**: Components should fail independently. System degradation should be graceful, not catastrophic.
 51|**Agent Guidance**: Design for failure isolation. When one component fails, others should continue operating.
 52|
 53|### CA-8. UI Process Separation
 54|**Rule**: UIs are separate processes consuming the capability API via a standardized interface.
 55|**Implementation**: 10-section sidebar structure: Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options.
 56|**Agent Guidance**: UI components must communicate via API. No direct core access from UI processes.
 57|
 58|### CA-9. Observability by Default
 59|**Rule**: No silent failures. All traces must be logged locally via TraceEmitter.
 60|**Implementation**: Every operation must emit trace data. Failures must be visible and actionable.
 61|**Agent Guidance**: Add trace emission to all new operations. Ensure failure modes are observable.
 62|
 63|### CA-10. Dependency Injection Only
 64|**Rule**: No global state or context bags. Maximum 15 constructor arguments per component.
 65|**Implementation**: Use constructor injection for all dependencies. Avoid static state or global variables.
 66|**Agent Guidance**: Pass dependencies explicitly via constructors. Keep constructor signatures focused.
 67|
 68|### CA-11. Strong and Robust
 69|**Rule**: Fail gracefully, isolate faults, recover without manual intervention.
 70|**Implementation**: Implement fault isolation, automatic recovery, and graceful degradation patterns.
 71|**Agent Guidance**: Design for failure scenarios. Implement automatic recovery where possible.
 72|
 73|## Development Principles (DP)
 74|
 75|### DP-1. Test-File Creation
 76|**Rule**: Every code file must have accompanying test files created simultaneously.
 77|**Implementation**: When creating implementation files, immediately create corresponding test files with initial test structure.
 78|**Agent Guidance**: Never create implementation files without test files. Test structure should mirror implementation structure.
 79|
 80|### DP-2. Modular Functionality
 81|**Rule**: Functions must be modular so that updates to one function don't break others.
 82|**Implementation**: Follow single responsibility principle. Minimize coupling between functions. Use clear interfaces.
 83|**Agent Guidance**: Design functions to be independent. Changes to one function should not require changes to others.
 84|
 85|### DP-3. Best Practices Compliance
 86|**Rule**: All code must follow established best practices for the language and framework.
 87|**Implementation**: Reference project-specific style guides and industry standards. Use linting and formatting tools.
 88|**Agent Guidance**: Check existing code patterns before implementing new code. Follow established conventions.
 89|
 90|### DP-4. Internal Implementation
 91|**Rule**: Create functionality internally rather than relying on external programs.
 92|**Implementation**: Prefer native implementation over shell commands or external process execution.
 93|**Agent Guidance**: Implement functionality directly in the codebase rather than calling external programs.
 94|
 95|## Operational Principles (OP)
 96|
 97|### OP-1. Comprehensive Logging
 98|**Rule**: Everything within execution must be logged and categorized.
 99|**Implementation**: Use structured logging with consistent categories. All operations must emit log events.
100|**Agent Guidance**: Add logging to all operations. Use standardized log categories for consistency.
101|
102|### OP-2. Best Practices Enforcement
103|**Rule**: Application must ensure best practices are followed for all components.
104|**Implementation**: Implement validation and compliance checking. Use automated tools where possible.
105|**Agent Guidance**: Include validation logic in the application layer. Prevent non-compliant code from executing.
106|
107|## Deferred Principles (DF)
108|
109|### DF-1. Security via Reasoning
110|**Rule**: Security Guard is a user-invoked tool, not an automatic gate.
111|**Status**: Deferred for future implementation.
112|**Implementation**: Security analysis should be available on-demand, not blocking normal operations.
113|
114|### DF-2. Provenance Enforcement
115|**Rule**: External components must have verifiable provenance.
116|**Status**: Deferred for future implementation.
117|**Implementation**: Implement component signing and verification for external plugins and extensions.
118|
119|---
120|
121|## Principle Reference Guide
122|
123|### Quick Reference by Category
124|- **Core Architecture (CA)**: CA-1 through CA-11 - System design and architecture
125|- **Development (DP)**: DP-1 through DP-4 - Coding practices and standards  
126|- **Operational (OP)**: OP-1 through OP-2 - Runtime behavior and logging
127|- **Deferred (DF)**: DF-1 through DF-2 - Future implementations
128|
129|### Agent-Specific Reference Mapping
130|- **Architect Agent**: Focus on CA-1 through CA-11 (Core Architecture)
131|- **Planner Agent**: Reference all principles for plan alignment
132|- **Executor Agent**: Focus on DP-1 through DP-4 (Development Principles)
133|- **Reviewer Agent**: Reference all principles for compliance verification
134|- **Researcher Agent**: Reference all principles for research context
135|
136|---
137|
138|## Principle Maintenance
139|
140|### Adding New Principles
141|1. Identify the appropriate category (CA, DP, OP, DF)
142|2. Assign next sequential number within that category
143|3. Write clear, agent-understandable language
144|4. Include implementation guidance for agents
145|5. Update version number and date
146|6. Maintain consistent formatting
147|
148|### Modifying Existing Principles
149|1. Update version number
150|2. Document rationale for changes
151|3. Ensure agent guidance remains clear
152|4. Update implementation examples if needed
153|5. Update reference mappings if category changes
154|
155|### Principle Review
156|Review principles quarterly for:
157|- Relevance to current system state
158|- Clarity for agent understanding
159|- Completeness of implementation guidance
160|- Consistency with actual system behavior
161|- Proper category assignment
162|
163|---
164|
165|**Note**: These principles are maintained by the Architect agent and serve as the single source of truth for SovereignAI architectural and operational decisions.
</file-view>
```

**Success**: True
**Tool Use ID**: call_cab51c8283014d8f898d5bac
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/PRINCIPLES.md"
  },
  "tool_use_id": "call_cab51c8283014d8f898d5bac",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/PRINCIPLES.md\" start_line=\"1\" end_line=\"165\" total_lines=\"165\">\n  1|# Principles \u00e2\u20ac\u201d SovereignAI\n  2|\n  3|**Version**: 3.0  \n  4|**Last Updated**: 2026-07-28  \n  5|**Maintained By**: Architect Agent  \n  6|**Purpose**: Architectural and operational principles that guide SovereignAI development decisions and implementation patterns\n  7|\n  8|---\n  9|\n 10|## Overview\n 11|\n 12|These principles govern the design, implementation, and operation of the SovereignAI system. They serve as the foundation for architectural decisions, development practices, and operational procedures. All agents and developers should reference these principles when making decisions about system changes or implementations.\n 13|\n 14|## Core Architecture Principles (CA)\n 15|\n 16|### CA-1. Core is Sacred\n 17|**Rule**: The system has exactly 12 core modules. All other functionality must be pluggable.\n 18|**Implementation**: Core modules provide essential system services. Any feature outside the core must be implemented as a pluggable component.\n 19|**Agent Guidance**: When adding new functionality, always implement as a pluggable component rather than modifying core modules.\n 20|\n 21|### CA-2. Everything Pluggable\n 22|**Rule**: All components are equal and interchangeable: adapters, skills, memory backends, models, UIs.\n 23|**Implementation**: Use consistent interfaces and dependency injection. No component should have special privileges or hardcoded dependencies.\n 24|**Agent Guidance**: Design new components with standardized interfaces that can be swapped without affecting system operation.\n 25|\n 26|### CA-3. No Provider Lock-in\n 27|**Rule**: System must continue operating if any single component is removed.\n 28|**Implementation**: Design for graceful degradation. Components should be hot-swappable without system restart.\n 29|**Agent Guidance**: Never create hard dependencies on specific providers. Always allow alternative implementations.\n 30|\n 31|### CA-4. Local-First\n 32|**Rule**: System runs fully offline. Cloud services are optional enhancements, not requirements.\n 33|**Implementation**: All core functionality must work without internet connectivity. Cloud features are opt-in escalations.\n 34|**Scope**: v1 supports Windows only.\n 35|**Agent Guidance**: Implement offline-first. Cloud features should be optional add-ons, not core dependencies.\n 36|\n 37|### CA-5. Wire as You Go\n 38|**Rule**: No speculative contracts or empty placeholder directories.\n 39|**Implementation**: Create components only when needed. Avoid premature abstraction or framework code.\n 40|**Agent Guidance**: Implement concrete functionality first. Add abstractions only when multiple implementations exist.\n 41|\n 42|### CA-6. One User, One System\n 43|**Rule**: Single user system accessible from anywhere. All UIs connect to the same core.\n 44|**Implementation**: Core is user-scoped. Multiple UI clients can connect to the same user's core instance.\n 45|**Deferred**: Phone/relay support.\n 46|**Agent Guidance**: Design for single-user multi-device access. Core state is per-user, not shared across users.\n 47|\n 48|### CA-7. Modular Over Simple\n 49|**Rule**: Prefer modular, flexible design over simple, monolithic approaches.\n 50|**Implementation**: Components should fail independently. System degradation should be graceful, not catastrophic.\n 51|**Agent Guidance**: Design for failure isolation. When one component fails, others should continue operating.\n 52|\n 53|### CA-8. UI Process Separation\n 54|**Rule**: UIs are separate processes consuming the capability API via a standardized interface.\n 55|**Implementation**: 10-section sidebar structure: Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options.\n 56|**Agent Guidance**: UI components must communicate via API. No direct core access from UI processes.\n 57|\n 58|### CA-9. Observability by Default\n 59|**Rule**: No silent failures. All traces must be logged locally via TraceEmitter.\n 60|**Implementation**: Every operation must emit trace data. Failures must be visible and actionable.\n 61|**Agent Guidance**: Add trace emission to all new operations. Ensure failure modes are observable.\n 62|\n 63|### CA-10. Dependency Injection Only\n 64|**Rule**: No global state or context bags. Maximum 15 constructor arguments per component.\n 65|**Implementation**: Use constructor injection for all dependencies. Avoid static state or global variables.\n 66|**Agent Guidance**: Pass dependencies explicitly via constructors. Keep constructor signatures focused.\n 67|\n 68|### CA-11. Strong and Robust\n 69|**Rule**: Fail gracefully, isolate faults, recover without manual intervention.\n 70|**Implementation**: Implement fault isolation, automatic recovery, and graceful degradation patterns.\n 71|**Agent Guidance**: Design for failure scenarios. Implement automatic recovery where possible.\n 72|\n 73|## Development Principles (DP)\n 74|\n 75|### DP-1. Test-File Creation\n 76|**Rule**: Every code file must have accompanying test files created simultaneously.\n 77|**Implementation**: When creating implementation files, immediately create corresponding test files with initial test structure.\n 78|**Agent Guidance**: Never create implementation files without test files. Test structure should mirror implementation structure.\n 79|\n 80|### DP-2. Modular Functionality\n 81|**Rule**: Functions must be modular so that updates to one function don't break others.\n 82|**Implementation**: Follow single responsibility principle. Minimize coupling between functions. Use clear interfaces.\n 83|**Agent Guidance**: Design functions to be independent. Changes to one function should not require changes to others.\n 84|\n 85|### DP-3. Best Practices Compliance\n 86|**Rule**: All code must follow established best practices for the language and framework.\n 87|**Implementation**: Reference project-specific style guides and industry standards. Use linting and formatting tools.\n 88|**Agent Guidance**: Check existing code patterns before implementing new code. Follow established conventions.\n 89|\n 90|### DP-4. Internal Implementation\n 91|**Rule**: Create functionality internally rather than relying on external programs.\n 92|**Implementation**: Prefer native implementation over shell commands or external process execution.\n 93|**Agent Guidance**: Implement functionality directly in the codebase rather than calling external programs.\n 94|\n 95|## Operational Principles (OP)\n 96|\n 97|### OP-1. Comprehensive Logging\n 98|**Rule**: Everything within execution must be logged and categorized.\n 99|**Implementation**: Use structured logging with consistent categories. All operations must emit log events.\n100|**Agent Guidance**: Add logging to all operations. Use standardized log categories for consistency.\n101|\n102|### OP-2. Best Practices Enforcement\n103|**Rule**: Application must ensure best practices are followed for all components.\n104|**Implementation**: Implement validation and compliance checking. Use automated tools where possible.\n105|**Agent Guidance**: Include validation logic in the application layer. Prevent non-compliant code from executing.\n106|\n107|## Deferred Principles (DF)\n108|\n109|### DF-1. Security via Reasoning\n110|**Rule**: Security Guard is a user-invoked tool, not an automatic gate.\n111|**Status**: Deferred for future implementation.\n112|**Implementation**: Security analysis should be available on-demand, not blocking normal operations.\n113|\n114|### DF-2. Provenance Enforcement\n115|**Rule**: External components must have verifiable provenance.\n116|**Status**: Deferred for future implementation.\n117|**Implementation**: Implement component signing and verification for external plugins and extensions.\n118|\n119|---\n120|\n121|## Principle Reference Guide\n122|\n123|### Quick Reference by Category\n124|- **Core Architecture (CA)**: CA-1 through CA-11 - System design and architecture\n125|- **Development (DP)**: DP-1 through DP-4 - Coding practices and standards  \n126|- **Operational (OP)**: OP-1 through OP-2 - Runtime behavior and logging\n127|- **Deferred (DF)**: DF-1 through DF-2 - Future implementations\n128|\n129|### Agent-Specific Reference Mapping\n130|- **Architect Agent**: Focus on CA-1 through CA-11 (Core Architecture)\n131|- **Planner Agent**: Reference all principles for plan alignment\n132|- **Executor Agent**: Focus on DP-1 through DP-4 (Development Principles)\n133|- **Reviewer Agent**: Reference all principles for compliance verification\n134|- **Researcher Agent**: Reference all principles for research context\n135|\n136|---\n137|\n138|## Principle Maintenance\n139|\n140|### Adding New Principles\n141|1. Identify the appropriate category (CA, DP, OP, DF)\n142|2. Assign next sequential number within that category\n143|3. Write clear, agent-understandable language\n144|4. Include implementation guidance for agents\n145|5. Update version number and date\n146|6. Maintain consistent formatting\n147|\n148|### Modifying Existing Principles\n149|1. Update version number\n150|2. Document rationale for changes\n151|3. Ensure agent guidance remains clear\n152|4. Update implementation examples if needed\n153|5. Update reference mappings if category changes\n154|\n155|### Principle Review\n156|Review principles quarterly for:\n157|- Relevance to current system state\n158|- Clarity for agent understanding\n159|- Completeness of implementation guidance\n160|- Consistency with actual system behavior\n161|- Proper category assignment\n162|\n163|---\n164|\n165|**Note**: These principles are maintained by the Architect agent and serve as the single source of truth for SovereignAI architectural and operational decisions.\n</file-view>",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:31.311872
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Workflow/Reviewer/Reviewer_Review_Workflow.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Reviewer/Reviewer_Review_Workflow.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:32.833389
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: glob
**Status**: attempt

**Input**:
```
{
  "pattern": "*.md",
  "path": "C:/SovereignAI/Workflow/Reviewer"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:32.968552
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: glob
**Status**: success
**Agent**: Reviewer

**Input**:
```
{
  "pattern": "*.md",
  "path": "C:/SovereignAI/Workflow/Reviewer"
}
```

**Output**:
```
C:/SovereignAI/Workflow/Reviewer\Reference\Compliance_Criteria_Reference.md
C:/SovereignAI/Workflow/Reviewer\Reference\Review_Mode_Patterns.md
C:/SovereignAI/Workflow/Reviewer\Reference\Subagent_Prompting_Reference.md
C:/SovereignAI/Workflow/Reviewer\Reference\Web_Search_Implementation_Guide.md
C:/SovereignAI/Workflow/Reviewer\Reviewer_BP_Scanner_Workflow.md
```

**Success**: True
**Tool Use ID**: call_6ee203cb6874476aaf009cd7
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "glob",
  "tool_input": {
    "pattern": "*.md",
    "path": "C:/SovereignAI/Workflow/Reviewer"
  },
  "tool_use_id": "call_6ee203cb6874476aaf009cd7",
  "tool_response": {
    "success": true,
    "output": "C:/SovereignAI/Workflow/Reviewer\\Reference\\Compliance_Criteria_Reference.md\nC:/SovereignAI/Workflow/Reviewer\\Reference\\Review_Mode_Patterns.md\nC:/SovereignAI/Workflow/Reviewer\\Reference\\Subagent_Prompting_Reference.md\nC:/SovereignAI/Workflow/Reviewer\\Reference\\Web_Search_Implementation_Guide.md\nC:/SovereignAI/Workflow/Reviewer\\Reviewer_BP_Scanner_Workflow.md",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:35.933507
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:46:35.934027
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:36.084232
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: success
**Agent**: Reviewer

**Input Summary**: File: C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md" start_line="1" end_line="202" total_lines="202">
  1|---
  2|id: wf-rev-ref-review-mode-patterns
  3|status: active
  4|owner: reviewer-agent
  5|updated: 2026-07-28
  6|purpose: Reviewer-specific execution mode patterns for comprehensive file scanning workflows
  7|---
  8|
  9|# Reviewer Execution Mode Patterns
 10|
 11|**Purpose**: Reviewer-specific execution mode patterns for comprehensive file scanning workflows.
 12|
 13|## Execution Mode Definitions
 14|
 15|### Manual Mode
 16|**Behavior**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight
 17|- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next file
 18|- **Failure Handling**: Stop workflow and await user intervention for retry/modify/abort decision
 19|- **User Control**: Maximum user control over file-by-file progression
 20|- **Risk Mitigation**: Human oversight at each file transition
 21|- **Use Case**: First comprehensive scan, high-risk files, learning phase
 22|
 23|### Manual Batched Mode
 24|**Behavior**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
 25|- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next batch
 26|- **Failure Handling**: Stop workflow and await user intervention if batch fails
 27|- **User Control**: Balanced user control with batch-level approval
 28|- **Risk Mitigation**: Human oversight at each batch transition with automated intra-batch processing
 29|- **Use Case**: Balanced efficiency with oversight, medium-risk scans
 30|
 31|### Automatic Mode
 32|**Behavior**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency
 33|- **Checkpoint Handling**: Proceed automatically to next file without user intervention
 34|- **Failure Handling**: Stop workflow automatically if a file fails (auto-stop on errors)
 35|- **User Control**: Minimal user control with maximum automated processing efficiency
 36|- **Risk Mitigation**: Automatic failure detection and stopping at file level
 37|- **Use Case**: Large codebases, established processes, maximum efficiency
 38|
 39|### Automatic Batched Mode
 40|**Behavior**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
 41|- **Checkpoint Handling**: Proceed automatically through all batches without user intervention
 42|- **Failure Handling**: Stop workflow automatically if a batch fails (auto-stop on errors)
 43|- **User Control**: Minimal user control with maximum automated processing efficiency
 44|- **Risk Mitigation**: Automatic failure detection and stopping at batch level
 45|- **Use Case**: Large codebases, established processes, maximum efficiency
 46|
 47|## Execution Mode Handling Patterns
 48|
 49|### Manual Mode Pattern
 50|1. **SCAN** single file line by line
 51|2. **{BP}** web search for current best practices (MANDATORY)
 52|3. Document findings to incremental report
 53|4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next file (CHECKPOINT)
 54|5. **STATUS TRACKING**: Update workflow status to "file_{N}_complete"
 55|6. **PRINT**: File completion message with checkpoint confirmation
 56|7. Wait for user approval before proceeding to next file
 57|
 58|### Manual Batched Mode Pattern
 59|1. **SCAN** batch of 5-10 files line by line
 60|2. **{BP}** web search for all files in batch (MANDATORY)
 61|3. Document findings to incremental report for all files
 62|4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next batch (CHECKPOINT)
 63|5. **STATUS TRACKING**: Update workflow status to "batch_{N}_complete"
 64|6. **PRINT**: Batch completion message with checkpoint confirmation
 65|7. Wait for user approval before proceeding to next batch
 66|
 67|### Automatic Mode Pattern
 68|1. **SCAN** single file line by line
 69|2. **{BP}** web search for current best practices (MANDATORY)
 70|3. Document findings to incremental report
 71|4. **EXECUTION MODE HANDLING**: Proceed automatically to next file if file succeeded, stop if file failed
 72|5. **STATUS TRACKING**: Update workflow status to "file_{N}_complete" (success) or "file_{N}_failed" (failure)
 73|6. **PRINT**: File completion message (success) or failure message with retry attempt information
 74|7. Proceed automatically to next file on success, apply retry logic on failure
 75|
 76|### Automatic Batched Mode Pattern
 77|1. **SCAN** batch of 5-10 files line by line
 78|2. **{BP}** web search for all files in batch (MANDATORY)
 79|3. Document findings to incremental report for all files
 80|4. **EXECUTION MODE HANDLING**: Proceed automatically to next batch if batch succeeded, stop if batch failed
 81|5. **STATUS TRACKING**: Update workflow status to "batch_{N}_complete" (success) or "batch_{N}_failed" (failure)
 82|6. **PRINT**: Batch completion message (success) or failure message with retry attempt information
 83|7. Proceed automatically to next batch on success, apply retry logic on failure
 84|
 85|## Failure Handling Patterns
 86|
 87|### Manual Mode Failure Pattern
 88|1. Detect failure in current file scan
 89|2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
 90|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval
 91|4. **STATUS TRACKING**: Update workflow status to "file_{N}_failed"
 92|5. **PRINT**: Failure message with file-level error details
 93|6. Await user decision on recovery action
 94|
 95|### Manual Batched Mode Failure Pattern
 96|1. Detect failure in current batch
 97|2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)
 98|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval
 99|4. **STATUS TRACKING**: Update workflow status to "batch_{N}_failed"
100|5. **PRINT**: Failure message with batch-level error details
101|6. Await user decision on recovery action
102|
103|### Automatic Mode Failure Pattern
104|1. Detect failure in current file scan
105|2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
106|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
107|4. **STATUS TRACKING**: Update workflow status to "file_{N}_failed"
108|5. **PRINT**: Failure message with retry attempt information
109|6. Proceed with retry logic automatically
110|
111|### Automatic Batched Mode Failure Pattern
112|1. Detect failure in current batch
113|2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention
114|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)
115|4. **STATUS TRACKING**: Update workflow status to "batch_{N}_failed"
116|5. **PRINT**: Failure message with retry attempt information
117|6. Proceed with retry logic automatically
118|
119|## Batch Configuration
120|
121|### Batch Size Configuration
122|- **Default Batch Size**: 5-10 files per batch
123|- **Batch Size Criteria**: Based on file complexity and token usage
124|- **Dynamic Adjustment**: Adjust batch size based on available context budget
125|- **Batch Logging**: Log each batch with file list and processing metadata
126|
127|### Batch Processing Order
128|- **Alphabetical Order**: Files processed in alphabetical order by full path
129|- **Batch Integrity**: All files in batch must complete before proceeding
130|- **Context Management**: PostCompaction hook reloads governance files when context is compressed
131|- **Incremental Documentation**: Findings documented immediately after each batch
132|
133|## Execution Mode Selection Guidelines
134|
135|### Manual Mode Selection
136|- First comprehensive scan of codebase
137|- High-risk or security-critical files
138|- Learning phase for new team members
139|- When detailed review of each file is required
140|- Unknown codebase or unfamiliar patterns
141|
142|### Manual Batched Mode Selection
143|- Established scanning process
144|- Medium-risk codebase
145|- Balance between efficiency and oversight
146|- Regular compliance scans
147|- When batch-level review is sufficient
148|
149|### Automatic Mode Selection
150|- Well-established scanning process
151|- Low-risk routine scans
152|- Time-constrained individual file processing
153|- When maximum efficiency for single files is required
154|
155|### Automatic Batched Mode Selection
156|- Large codebases (>150 files)
157|- Well-established scanning process
158|- Low-risk routine scans
159|- Time-constrained comprehensive scans
160|- When maximum efficiency is required
161|
162|## Retry Logic with Exponential Backoff
163|
164|### Retry Configuration
165|- **Max Retries**: 3 retries maximum
166|- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)
167|- **Retry Criteria**: Configurable based on error type
168|- **Retry Logging**: Log each retry attempt with metadata
169|- **Batch Retry**: For batched modes, retry entire batch or individual items based on failure scope
170|
171|### Retry Implementation
172|```python
173|retry_count = 0
174|max_retries = 3
175|backoff_time = 1
176|
177|while retry_count < max_retries:
178|    try:
179|        # Execute file or batch scan
180|        execute_scan()
181|        break  # Success, exit retry loop
182|    except Exception as error:
183|        retry_count += 1
184|        if retry_count >= max_retries:
185|            raise  # Max retries reached
186|        time.sleep(backoff_time)
187|        backoff_time *= 2  # Exponential backoff
188|```
189|
190|## State Management
191|
192|### Mode Storage
193|- **Mode Storage**: Store selected execution mode in workflow state
194|- **Batch Size**: Store configured batch size for consistency
195|- **Current Batch**: Track current batch number and file indices
196|- **Failure Context**: Store failure context for retry logic
197|
198|### Audit Trail
199|- **Mode Selection**: Log mode selection with reasoning
200|- **Batch Processing**: Log each batch with file list and outcomes
201|- **Failure Handling**: Log failure handling patterns and recovery actions
202|- **User Checkpoints**: Log user checkpoint decisions in Manual modes
</file-view>
```

**Success**: True
**Tool Use ID**: call_9181cccbf8084b55b49bea76
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md"
  },
  "tool_use_id": "call_9181cccbf8084b55b49bea76",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Workflow/Reviewer/Reference/Review_Mode_Patterns.md\" start_line=\"1\" end_line=\"202\" total_lines=\"202\">\n  1|---\n  2|id: wf-rev-ref-review-mode-patterns\n  3|status: active\n  4|owner: reviewer-agent\n  5|updated: 2026-07-28\n  6|purpose: Reviewer-specific execution mode patterns for comprehensive file scanning workflows\n  7|---\n  8|\n  9|# Reviewer Execution Mode Patterns\n 10|\n 11|**Purpose**: Reviewer-specific execution mode patterns for comprehensive file scanning workflows.\n 12|\n 13|## Execution Mode Definitions\n 14|\n 15|### Manual Mode\n 16|**Behavior**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight\n 17|- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next file\n 18|- **Failure Handling**: Stop workflow and await user intervention for retry/modify/abort decision\n 19|- **User Control**: Maximum user control over file-by-file progression\n 20|- **Risk Mitigation**: Human oversight at each file transition\n 21|- **Use Case**: First comprehensive scan, high-risk files, learning phase\n 22|\n 23|### Manual Batched Mode\n 24|**Behavior**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches\n 25|- **Checkpoint Handling**: Require user confirmation via popup menu before proceeding to each next batch\n 26|- **Failure Handling**: Stop workflow and await user intervention if batch fails\n 27|- **User Control**: Balanced user control with batch-level approval\n 28|- **Risk Mitigation**: Human oversight at each batch transition with automated intra-batch processing\n 29|- **Use Case**: Balanced efficiency with oversight, medium-risk scans\n 30|\n 31|### Automatic Mode\n 32|**Behavior**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency\n 33|- **Checkpoint Handling**: Proceed automatically to next file without user intervention\n 34|- **Failure Handling**: Stop workflow automatically if a file fails (auto-stop on errors)\n 35|- **User Control**: Minimal user control with maximum automated processing efficiency\n 36|- **Risk Mitigation**: Automatic failure detection and stopping at file level\n 37|- **Use Case**: Large codebases, established processes, maximum efficiency\n 38|\n 39|### Automatic Batched Mode\n 40|**Behavior**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation\n 41|- **Checkpoint Handling**: Proceed automatically through all batches without user intervention\n 42|- **Failure Handling**: Stop workflow automatically if a batch fails (auto-stop on errors)\n 43|- **User Control**: Minimal user control with maximum automated processing efficiency\n 44|- **Risk Mitigation**: Automatic failure detection and stopping at batch level\n 45|- **Use Case**: Large codebases, established processes, maximum efficiency\n 46|\n 47|## Execution Mode Handling Patterns\n 48|\n 49|### Manual Mode Pattern\n 50|1. **SCAN** single file line by line\n 51|2. **{BP}** web search for current best practices (MANDATORY)\n 52|3. Document findings to incremental report\n 53|4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next file (CHECKPOINT)\n 54|5. **STATUS TRACKING**: Update workflow status to \"file_{N}_complete\"\n 55|6. **PRINT**: File completion message with checkpoint confirmation\n 56|7. Wait for user approval before proceeding to next file\n 57|\n 58|### Manual Batched Mode Pattern\n 59|1. **SCAN** batch of 5-10 files line by line\n 60|2. **{BP}** web search for all files in batch (MANDATORY)\n 61|3. Document findings to incremental report for all files\n 62|4. **EXECUTION MODE HANDLING**: Require user confirmation via popup menu before proceeding to next batch (CHECKPOINT)\n 63|5. **STATUS TRACKING**: Update workflow status to \"batch_{N}_complete\"\n 64|6. **PRINT**: Batch completion message with checkpoint confirmation\n 65|7. Wait for user approval before proceeding to next batch\n 66|\n 67|### Automatic Mode Pattern\n 68|1. **SCAN** single file line by line\n 69|2. **{BP}** web search for current best practices (MANDATORY)\n 70|3. Document findings to incremental report\n 71|4. **EXECUTION MODE HANDLING**: Proceed automatically to next file if file succeeded, stop if file failed\n 72|5. **STATUS TRACKING**: Update workflow status to \"file_{N}_complete\" (success) or \"file_{N}_failed\" (failure)\n 73|6. **PRINT**: File completion message (success) or failure message with retry attempt information\n 74|7. Proceed automatically to next file on success, apply retry logic on failure\n 75|\n 76|### Automatic Batched Mode Pattern\n 77|1. **SCAN** batch of 5-10 files line by line\n 78|2. **{BP}** web search for all files in batch (MANDATORY)\n 79|3. Document findings to incremental report for all files\n 80|4. **EXECUTION MODE HANDLING**: Proceed automatically to next batch if batch succeeded, stop if batch failed\n 81|5. **STATUS TRACKING**: Update workflow status to \"batch_{N}_complete\" (success) or \"batch_{N}_failed\" (failure)\n 82|6. **PRINT**: Batch completion message (success) or failure message with retry attempt information\n 83|7. Proceed automatically to next batch on success, apply retry logic on failure\n 84|\n 85|## Failure Handling Patterns\n 86|\n 87|### Manual Mode Failure Pattern\n 88|1. Detect failure in current file scan\n 89|2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)\n 90|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval\n 91|4. **STATUS TRACKING**: Update workflow status to \"file_{N}_failed\"\n 92|5. **PRINT**: Failure message with file-level error details\n 93|6. Await user decision on recovery action\n 94|\n 95|### Manual Batched Mode Failure Pattern\n 96|1. Detect failure in current batch\n 97|2. **EXECUTION MODE HANDLING**: Stop workflow and await user intervention for retry/modify/abort decision (CHECKPOINT)\n 98|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries) upon user approval\n 99|4. **STATUS TRACKING**: Update workflow status to \"batch_{N}_failed\"\n100|5. **PRINT**: Failure message with batch-level error details\n101|6. Await user decision on recovery action\n102|\n103|### Automatic Mode Failure Pattern\n104|1. Detect failure in current file scan\n105|2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention\n106|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)\n107|4. **STATUS TRACKING**: Update workflow status to \"file_{N}_failed\"\n108|5. **PRINT**: Failure message with retry attempt information\n109|6. Proceed with retry logic automatically\n110|\n111|### Automatic Batched Mode Failure Pattern\n112|1. Detect failure in current batch\n113|2. **EXECUTION MODE HANDLING**: Stop workflow automatically without requiring human intervention\n114|3. **RETRY LOGIC**: Implement configurable retry with exponential backoff (max 3 retries)\n115|4. **STATUS TRACKING**: Update workflow status to \"batch_{N}_failed\"\n116|5. **PRINT**: Failure message with retry attempt information\n117|6. Proceed with retry logic automatically\n118|\n119|## Batch Configuration\n120|\n121|### Batch Size Configuration\n122|- **Default Batch Size**: 5-10 files per batch\n123|- **Batch Size Criteria**: Based on file complexity and token usage\n124|- **Dynamic Adjustment**: Adjust batch size based on available context budget\n125|- **Batch Logging**: Log each batch with file list and processing metadata\n126|\n127|### Batch Processing Order\n128|- **Alphabetical Order**: Files processed in alphabetical order by full path\n129|- **Batch Integrity**: All files in batch must complete before proceeding\n130|- **Context Management**: PostCompaction hook reloads governance files when context is compressed\n131|- **Incremental Documentation**: Findings documented immediately after each batch\n132|\n133|## Execution Mode Selection Guidelines\n134|\n135|### Manual Mode Selection\n136|- First comprehensive scan of codebase\n137|- High-risk or security-critical files\n138|- Learning phase for new team members\n139|- When detailed review of each file is required\n140|- Unknown codebase or unfamiliar patterns\n141|\n142|### Manual Batched Mode Selection\n143|- Established scanning process\n144|- Medium-risk codebase\n145|- Balance between efficiency and oversight\n146|- Regular compliance scans\n147|- When batch-level review is sufficient\n148|\n149|### Automatic Mode Selection\n150|- Well-established scanning process\n151|- Low-risk routine scans\n152|- Time-constrained individual file processing\n153|- When maximum efficiency for single files is required\n154|\n155|### Automatic Batched Mode Selection\n156|- Large codebases (>150 files)\n157|- Well-established scanning process\n158|- Low-risk routine scans\n159|- Time-constrained comprehensive scans\n160|- When maximum efficiency is required\n161|\n162|## Retry Logic with Exponential Backoff\n163|\n164|### Retry Configuration\n165|- **Max Retries**: 3 retries maximum\n166|- **Backoff Pattern**: Exponential backoff (1s, 2s, 4s, 8s, etc.)\n167|- **Retry Criteria**: Configurable based on error type\n168|- **Retry Logging**: Log each retry attempt with metadata\n169|- **Batch Retry**: For batched modes, retry entire batch or individual items based on failure scope\n170|\n171|### Retry Implementation\n172|```python\n173|retry_count = 0\n174|max_retries = 3\n175|backoff_time = 1\n176|\n177|while retry_count < max_retries:\n178|    try:\n179|        # Execute file or batch scan\n180|        execute_scan()\n181|        break  # Success, exit retry loop\n182|    except Exception as error:\n183|        retry_count += 1\n184|        if retry_count >= max_retries:\n185|            raise  # Max retries reached\n186|        time.sleep(backoff_time)\n187|        backoff_time *= 2  # Exponential backoff\n188|```\n189|\n190|## State Management\n191|\n192|### Mode Storage\n193|- **Mode Storage**: Store selected execution mode in workflow state\n194|- **Batch Size**: Store configured batch size for consistency\n195|- **Current Batch**: Track current batch number and file indices\n196|- **Failure Context**: Store failure context for retry logic\n197|\n198|### Audit Trail\n199|- **Mode Selection**: Log mode selection with reasoning\n200|- **Batch Processing**: Log each batch with file list and outcomes\n201|- **Failure Handling**: Log failure handling patterns and recovery actions\n202|- **User Checkpoints**: Log user checkpoint decisions in Manual modes\n</file-view>",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:46:36.214892
**Session**: sphenoid-field
**Prompt ID**: 30058767-740d-4469-adef-2d6935c5bb8e
**Tool**: read
**Status**: success
**Agent**: Reviewer

**Input Summary**: File: C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md" start_line="1" end_line="244" total_lines="263">
  1|---
  2|id: wf-rev-bp-scanner
  3|status: active
  4|owner: reviewer-agent
  5|updated: 2026-07-28
  6|purpose: Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency
  7|---
  8|
  9|# Reviewer BP Scanner Workflow (Unified)
 10|
 11|**ID**: WF-REV-BP-001  
 12|**Owner**: Reviewer Agent  
 13|**Frequency**: On-demand  
 14|**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
 15|**Priority**: High
 16|**Workflow Type**: Single-Execution (Utility Workflow)
 17|**Execution Modes**: Manual, Manual Batched, Automatic, Automatic Batched
 18|
 19|## Purpose
 20|Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against current best practices without exception, with mandatory **{BP}** web search for each file to ensure compliance with the latest industry standards. This process is designed to be comprehensive and token-intensive, prioritizing thoroughness over speed.
 21|
 22|## Scope
 23|**Two Scanning Modes**:
 24|- **App Mode**: All files in App/ directory (application code scanning)
 25|- **Harness Mode**: All files in project directory EXCLUDING App/, Logs/, Plans/, Docs/ folders (governance scanning)
 26|
 27|**SCAN-REPORT Locations**:
 28|- **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
 29|- **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
 30|
 31|## Reference Files (SSOT)
 32|- **Compliance Criteria**: Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md (detailed compliance requirements by file type)
 33|- **Subagent Prompting**: Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (subagent prompt templates and patterns)
 34|- **Web Search Implementation**: Workflow/Reviewer/Reference/Web_Search_Implementation_Guide.md (robust web search infrastructure)
 35|
 36|## Roles and Owners
 37|- **Reviewer Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
 38|- **User**: Requests scanning, selects scanning mode, approves findings and recommendations
 39|- **Governance System**: Validation against governance best practices and architectural standards
 40|
 41|## Trigger and End State
 42|- **Trigger**: User requests best practice compliance scan
 43|- **End State**: Single comprehensive SCAN-REPORT with findings, severity ratings, and actionable recommendations
 44|
 45|## Workflow Steps (81 steps)
 46|
 47|### Phase 0. Load Governance Rules
 48|- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
 49|- 2. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
 50|- 3. **PRINT** "Governance rules loaded dynamically based on agent type"
 51|
 52|### Phase 1. Select Scanning Mode
 53|- 1. Ask user to select scanning mode using popup menu:
 54|  - **App Mode**: Scan App/ directory only (application code scanning)
 55|  - **Harness Mode**: Scan harness governance files (excludes App/, Logs/, Plans/, Docs/)
 56|- 2. Store selected scanning mode for scope definition throughout workflow
 57|- 3. **PRINT** "Scanning mode selected - [App Mode/Harness Mode] will govern scan scope and log locations"
 58|
 59|### Phase 2. Select Execution Mode
 60|- 1. Ask user to select execution mode for this workflow using popup menu:
 61|  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)
 62|  - **Manual Batched**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches for balanced efficiency with oversight
 63|  - **Automatic**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency
 64|  - **Automatic Batched**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation for maximum efficiency
 65|- 2. Store selected execution mode for file processing strategy throughout workflow
 66|- 3. **PRINT** "Execution mode selected - [Manual/Manual Batched/Automatic/Automatic Batched] will govern file processing strategy"
 67|
 68|### Phase 3. Scan Scope Definition
 69|- 1. **IF App Mode**: Define scan scope as App/ directory (every single file - no exceptions)
 70|- 2. **IF Harness Mode**: Define scan scope as all files in project directory (excluding App/, Logs/, Plans/, Docs/ folders)
 71|- 3. Ask user to select subagent strategy using popup menu:
 72|  - **Use Subagents**: Delegate scanning to subagents for large-scale processing
 73|  - **Direct Scanning**: Reviewer agent scans all files directly (recommended for smaller file counts)
 74|- 4. Store selected subagent strategy for file processing throughout workflow
 75|- 5. **CRITICAL REQUIREMENT**: Every single file must be checked against best practices - no file may be skipped
 76|- 6. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
 77|- 7. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
 78|- 8. **IF App Mode**: **PRINT** "Scan scope defined - App/ directory comprehensive compliance verification - every file will be examined"
 79|- 9. **IF Harness Mode**: **PRINT** "Scan scope defined - Harness governance comprehensive compliance verification - every governance file will be examined"
 80|
 81|### Phase 4. File Discovery + Categorization (Alphabetical Order)
 82|- 1. Discover every single file based on scanning mode:
 83|  - **App Mode**: Execute `find App -type f` to discover every single file in App/ directory (209 files expected) - verify no files are missed
 84|  - **Harness Mode**: Execute `find . -type f ! -path "*/App/*" ! -path "*/Logs/*" ! -path "*/Plans/*" ! -path "*/Docs/*" ! -path "*/.git/*"` to discover every single file in project directory excluding specified folders (173 files expected)
 85|- 2. **CRITICAL REQUIREMENT**: Verify file count matches expected values:
 86|  - **App Mode**: Should discover exactly 209 files
 87|  - **Harness Mode**: Should discover exactly 173 files
 88|  - **CRITICAL**: If file count doesn't match expected values, halt workflow and investigate discrepancy
 89|- 3. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
 90|- 4. Categorize each file by module and complexity with detailed analysis:
 91|  - **App Mode**: Memory components, Agent system components, Messaging/event system, Model registry components, Orchestrator components, Skills/adapters integration, Configuration files, Documentation files
 92|  - **Harness Mode**: Workflow files, Rules files, Configuration files, Governance files, Script files, Data files, Documentation files
 93|- 5. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope
 94|- 6. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception
 95|- 7. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
 96|- 8. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
 97|- 9. **IF App Mode**: **PRINT** "File discovery complete - [N] files categorized by module and sorted alphabetically - file count verification passed - every file will be examined against best practices in chronological order"
 98|- 10. **IF Harness Mode**: **PRINT** "File discovery complete - [N] governance files categorized by type and sorted alphabetically - file count verification passed - every governance file will be examined against best practices in chronological order"
 99|
100|### Phase 5. Compliance Scanning Execution (Execution Mode Dependent)
101|- 1. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
102|- 2. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
103|- 3. **IF Automatic mode**: Process files one by one in alphabetical order automatically without user confirmation
104|- 4. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
105|- 5. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against best practices - no file may be skipped
106|- 6. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
107|- 7. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 4
108|- 8. **INFRASTRUCTURE SETUP**: Initialize efficient report writer based on scanning mode:
109|  - **App Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/App SCAN-REPORT
110|  - **Harness Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/Harness SCAN-REPORT
111|- 9. **WEB SEARCH ROBUSTNESS**: Use robust web search with caching and rate limiting based on scanning mode:
112|  - **App Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/App/Cache/WebSearch
113|  - **Harness Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/Harness/Cache/WebSearch
114|- 10. **VERBOSE OUTPUT**: Use **PRINT** commands after each file scan to maintain user visibility into progress, and explicitly output web search results to chat (not just to report) for maximum transparency
115|- 11. **EXECUTION MODE SPECIFIC PROCESS**:
116|  - **Manual**: For each file individually: **SCAN** â†’ **{BP}** web search â†’ output web search results to chat â†’ document findings â†’ **PRINT** progress â†’ user confirmation â†’ next file
117|  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch â†’ **{BP}** web search for all files â†’ output web search results to chat â†’ document findings â†’ **PRINT** progress â†’ user confirmation â†’ next batch
118|  - **Automatic**: For each file individually: **SCAN** â†’ **{BP}** web search â†’ output web search results to chat â†’ document findings â†’ **PRINT** progress â†’ next file (auto-stop on errors)
119|  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch â†’ **{BP}** web search for all files â†’ output web search results to chat â†’ document findings â†’ **PRINT** progress â†’ next batch (auto-stop on errors)
120|- 12. For each file, verify compliance criteria based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md as SSOT for detailed requirements
121|- 13. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to report file
122|- 14. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format using Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md as SSOT for prompting patterns
123|- 15. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single file without exception
124|- 16. **VALIDATION**: Validate that **{BP}** web search was performed for every single file without exception
125|- 17. **VALIDATION**: Validate that findings were documented to report file after each file/batch scan
126|- 18. **VALIDATION**: Validate that files were processed in alphabetical order
127|- 19. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
128|- 20. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
129|- 21. **IF App Mode**: **PRINT** "Compliance scanning complete - [N] files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"
130|- 22. **IF Harness Mode**: **PRINT** "Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"
131|
132|### Phase 6. Findings Consolidation (Scan Report Processing)
133|- 1. Collect all scanning results from SCAN-REPORT file based on scanning mode:
134|  - **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
135|  - **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
136|- 2. Consolidate findings by category and severity using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md severity classifications
137|- 3. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file in SCAN-REPORT - no file may be left unexamined or unreported
138|- 4. Cross-validate findings to eliminate duplicates and ensure consistency across all files
139|- 5. **VALIDATION**: Validate that findings consolidation completed successfully for every single file
140|- 6. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
141|- 7. **IF App Mode**: **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] files - every file examined"
142|- 8. **IF Harness Mode**: **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] governance files - every governance file examined"
143|
144|### Phase 7. Compliance Report Generation
145|- 1. Consolidate SCAN-REPORT to include comprehensive compliance analysis:
146|  - Executive summary (overall compliance score, critical findings count, files examined)
147|  - Detailed findings by file with line numbers and specific violations for each file
148|  - Severity ratings with context for why each issue matters per file
149|  - Actionable recommendations with clear improvement paths per file
150|  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file
151|- 2. **CRITICAL REQUIREMENT**: Ensure SCAN-REPORT includes analysis for every single file - no file may be omitted from the report
152|- 3. **CRITICAL REQUIREMENT**: SCAN-REPORT is the single comprehensive report - no separate files needed
153|- 4. **VALIDATION**: Validate that SCAN-REPORT consolidation completed successfully and every file is included
154|- 5. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
155|- 6. **IF App Mode**: **PRINT** "SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/App/ - includes detailed analysis for every single file"
156|- 7. **IF Harness Mode**: **PRINT** "SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/Harness/ - includes detailed analysis for every single governance file"
157|
158|### Phase 8. Final Validation + User Review
159|- 1. Verify report completeness and accuracy
160|- 2. Ensure all findings are properly documented with specific references
161|- 3. Check that recommendations are actionable and clear
162|- 4. **VALIDATION**: Validate that final validation completed successfully
163|- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
164|- 6. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
165|- 7. **PRINT** "Final validation complete - compliance report ready for user review"
166|
167|### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
168|- 1. **PRINT** "Best Practice Scanner workflow execution complete - workflow terminated"
169|- 2. **IF App Mode**: **PRINT** "Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/App/ for review and action"
170|- 3. **IF Harness Mode**: **PRINT** "Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/Harness/ for review and action"
171|- 4. **TERMINATE**: End workflow execution (do not return to step 1)
172|
173|---
174|
175|## Universal Framework References
176|
177|### Quality Assessment
178|- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
179|- **Reviewer Customization**: Reviewer-specific quality criteria for compliance verification
180|- **Focus**: Compliance quality assessment with governance verification
181|
182|### Validation Enforcement
183|- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
184|- **Reviewer Customization**: Reviewer-specific validation patterns for scanning verification
185|- **Focus**: Scanning validation and findings verification
186|
187|### Execution Strategy
188|- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
189|- **Reviewer Customization**: Reviewer-specific execution patterns for large-scale scanning
190|- **Focus**: Subagent coordination and failure handling during comprehensive scanning
191|
192|### State Management
193|- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
194|- **Reviewer Customization**: Reviewer-specific state tracking for scanning progress
195|- **Focus**: Scanning progress tracking and findings consolidation state management
196|
197|### Review Mode Patterns
198|- **Reviewer-Specific Framework**: Workflow/Reviewer/Reference/Review_Mode_Patterns.md
199|- **Reviewer Customization**: Reviewer-specific execution mode patterns for comprehensive code review
200|- **Focus**: Step-by-step review oversight, file-by-file review patterns, subagent coordination
201|
202|## Subagent Prompting Strategy
203|
204|### Large-Scale Scanning Approach
205|For large-scale scanning (>150 files), use parallel subagents by module/category following the prompting patterns and templates defined in Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (SSOT for subagent prompting).
206|
207|### Subagent Coordination
208|- Launch 4-5 parallel subagents for independent module/categories
209|- Each subagent receives precise scope with specific file list
210|- Define exact output format for consistent consolidation
211|- Validate subagent results against compliance standards
212|- Consolidate findings into comprehensive report
213|
214|## Scan Complexity Assessment
215|
216|Based on scanning mode:
217|- **App Mode**: 209 files expected (application code scanning)
218|- **Harness Mode**: 173 files expected (governance files scanning)
219|- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
220|- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module/category
221|- **Estimated Duration**: Extended (mandatory **{BP}** web search for each file)
222|- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per file)
223|- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per file
224|- **Process**: **SCAN** file (alphabetical order) â†’ **{BP}** web search â†’ **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) â†’ Next file (repeat for all files)
225|- **Final Output**: Single comprehensive SCAN-REPORT containing all findings, analysis, and recommendations
226|- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process
227|
228|## Execution Mode Recommendations
229|
230|- **Manual Mode**: Recommended for comprehensive scan to review each **{BP}** web search result and file analysis as it completes for maximum oversight
231|- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 files at a time with confirmation between batches
232|- **Automatic Batched Mode**: Maximum efficiency for large codebases - processes 5-10 files at a time automatically without confirmation
233|
234|**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each file undergoes: **SCAN** (line-by-line examination) â†’ **{BP}** (mandatory web search for current best practices) â†’ **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) â†’ Next file. The final SCAN-REPORT serves as the single comprehensive report containing all findings, analysis, and recommendations. This process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.
235|
236|## Context Management Strategy
237|
238|### PostCompaction Hook Configuration
239|- **Hook File**: .devin/hooks.v1.json
240|- **Purpose**: Reload governance files when context is compressed
241|- **Configuration**: Ensure PostCompaction hook is configured to reload:
242|  - Rules/Reviewer/Reviewer_Rules.md
243|  - PRINCIPLES.md
244|  - Workflow/Workflow_Reference/Terminology_Glossary.md
</file-view>
```

**Success**: True
**Tool Use ID**: call_369a91032a4e4696bb634d82
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md"
  },
  "tool_use_id": "call_369a91032a4e4696bb634d82",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Workflow/Reviewer/Reviewer_BP_Scanner_Workflow.md\" start_line=\"1\" end_line=\"244\" total_lines=\"263\">\n  1|---\n  2|id: wf-rev-bp-scanner\n  3|status: active\n  4|owner: reviewer-agent\n  5|updated: 2026-07-28\n  6|purpose: Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency\n  7|---\n  8|\n  9|# Reviewer BP Scanner Workflow (Unified)\n 10|\n 11|**ID**: WF-REV-BP-001  \n 12|**Owner**: Reviewer Agent  \n 13|**Frequency**: On-demand  \n 14|**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  \n 15|**Priority**: High\n 16|**Workflow Type**: Single-Execution (Utility Workflow)\n 17|**Execution Modes**: Manual, Manual Batched, Automatic, Automatic Batched\n 18|\n 19|## Purpose\n 20|Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against current best practices without exception, with mandatory **{BP}** web search for each file to ensure compliance with the latest industry standards. This process is designed to be comprehensive and token-intensive, prioritizing thoroughness over speed.\n 21|\n 22|## Scope\n 23|**Two Scanning Modes**:\n 24|- **App Mode**: All files in App/ directory (application code scanning)\n 25|- **Harness Mode**: All files in project directory EXCLUDING App/, Logs/, Plans/, Docs/ folders (governance scanning)\n 26|\n 27|**SCAN-REPORT Locations**:\n 28|- **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md\n 29|- **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md\n 30|\n 31|## Reference Files (SSOT)\n 32|- **Compliance Criteria**: Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md (detailed compliance requirements by file type)\n 33|- **Subagent Prompting**: Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (subagent prompt templates and patterns)\n 34|- **Web Search Implementation**: Workflow/Reviewer/Reference/Web_Search_Implementation_Guide.md (robust web search infrastructure)\n 35|\n 36|## Roles and Owners\n 37|- **Reviewer Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings\n 38|- **User**: Requests scanning, selects scanning mode, approves findings and recommendations\n 39|- **Governance System**: Validation against governance best practices and architectural standards\n 40|\n 41|## Trigger and End State\n 42|- **Trigger**: User requests best practice compliance scan\n 43|- **End State**: Single comprehensive SCAN-REPORT with findings, severity ratings, and actionable recommendations\n 44|\n 45|## Workflow Steps (81 steps)\n 46|\n 47|### Phase 0. Load Governance Rules\n 48|- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type\n 49|- 2. **STATUS TRACKING**: Update workflow status to \"phase_0_complete\"\n 50|- 3. **PRINT** \"Governance rules loaded dynamically based on agent type\"\n 51|\n 52|### Phase 1. Select Scanning Mode\n 53|- 1. Ask user to select scanning mode using popup menu:\n 54|  - **App Mode**: Scan App/ directory only (application code scanning)\n 55|  - **Harness Mode**: Scan harness governance files (excludes App/, Logs/, Plans/, Docs/)\n 56|- 2. Store selected scanning mode for scope definition throughout workflow\n 57|- 3. **PRINT** \"Scanning mode selected - [App Mode/Harness Mode] will govern scan scope and log locations\"\n 58|\n 59|### Phase 2. Select Execution Mode\n 60|- 1. Ask user to select execution mode for this workflow using popup menu:\n 61|  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)\n 62|  - **Manual Batched**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches for balanced efficiency with oversight\n 63|  - **Automatic**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency\n 64|  - **Automatic Batched**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation for maximum efficiency\n 65|- 2. Store selected execution mode for file processing strategy throughout workflow\n 66|- 3. **PRINT** \"Execution mode selected - [Manual/Manual Batched/Automatic/Automatic Batched] will govern file processing strategy\"\n 67|\n 68|### Phase 3. Scan Scope Definition\n 69|- 1. **IF App Mode**: Define scan scope as App/ directory (every single file - no exceptions)\n 70|- 2. **IF Harness Mode**: Define scan scope as all files in project directory (excluding App/, Logs/, Plans/, Docs/ folders)\n 71|- 3. Ask user to select subagent strategy using popup menu:\n 72|  - **Use Subagents**: Delegate scanning to subagents for large-scale processing\n 73|  - **Direct Scanning**: Reviewer agent scans all files directly (recommended for smaller file counts)\n 74|- 4. Store selected subagent strategy for file processing throughout workflow\n 75|- 5. **CRITICAL REQUIREMENT**: Every single file must be checked against best practices - no file may be skipped\n 76|- 6. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)\n 77|- 7. **STATUS TRACKING**: Update workflow status to \"phase_3_complete\"\n 78|- 8. **IF App Mode**: **PRINT** \"Scan scope defined - App/ directory comprehensive compliance verification - every file will be examined\"\n 79|- 9. **IF Harness Mode**: **PRINT** \"Scan scope defined - Harness governance comprehensive compliance verification - every governance file will be examined\"\n 80|\n 81|### Phase 4. File Discovery + Categorization (Alphabetical Order)\n 82|- 1. Discover every single file based on scanning mode:\n 83|  - **App Mode**: Execute `find App -type f` to discover every single file in App/ directory (209 files expected) - verify no files are missed\n 84|  - **Harness Mode**: Execute `find . -type f ! -path \"*/App/*\" ! -path \"*/Logs/*\" ! -path \"*/Plans/*\" ! -path \"*/Docs/*\" ! -path \"*/.git/*\"` to discover every single file in project directory excluding specified folders (173 files expected)\n 85|- 2. **CRITICAL REQUIREMENT**: Verify file count matches expected values:\n 86|  - **App Mode**: Should discover exactly 209 files\n 87|  - **Harness Mode**: Should discover exactly 173 files\n 88|  - **CRITICAL**: If file count doesn't match expected values, halt workflow and investigate discrepancy\n 89|- 3. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)\n 90|- 4. Categorize each file by module and complexity with detailed analysis:\n 91|  - **App Mode**: Memory components, Agent system components, Messaging/event system, Model registry components, Orchestrator components, Skills/adapters integration, Configuration files, Documentation files\n 92|  - **Harness Mode**: Workflow files, Rules files, Configuration files, Governance files, Script files, Data files, Documentation files\n 93|- 5. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope\n 94|- 6. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception\n 95|- 7. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order\n 96|- 8. **STATUS TRACKING**: Update workflow status to \"phase_4_complete\"\n 97|- 9. **IF App Mode**: **PRINT** \"File discovery complete - [N] files categorized by module and sorted alphabetically - file count verification passed - every file will be examined against best practices in chronological order\"\n 98|- 10. **IF Harness Mode**: **PRINT** \"File discovery complete - [N] governance files categorized by type and sorted alphabetically - file count verification passed - every governance file will be examined against best practices in chronological order\"\n 99|\n100|### Phase 5. Compliance Scanning Execution (Execution Mode Dependent)\n101|- 1. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding\n102|- 2. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches\n103|- 3. **IF Automatic mode**: Process files one by one in alphabetical order automatically without user confirmation\n104|- 4. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation\n105|- 5. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against best practices - no file may be skipped\n106|- 6. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file\n107|- 7. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 4\n108|- 8. **INFRASTRUCTURE SETUP**: Initialize efficient report writer based on scanning mode:\n109|  - **App Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/App SCAN-REPORT\n110|  - **Harness Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/Harness SCAN-REPORT\n111|- 9. **WEB SEARCH ROBUSTNESS**: Use robust web search with caching and rate limiting based on scanning mode:\n112|  - **App Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/App/Cache/WebSearch\n113|  - **Harness Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/Harness/Cache/WebSearch\n114|- 10. **VERBOSE OUTPUT**: Use **PRINT** commands after each file scan to maintain user visibility into progress, and explicitly output web search results to chat (not just to report) for maximum transparency\n115|- 11. **EXECUTION MODE SPECIFIC PROCESS**:\n116|  - **Manual**: For each file individually: **SCAN** \u00e2\u2020\u2019 **{BP}** web search \u00e2\u2020\u2019 output web search results to chat \u00e2\u2020\u2019 document findings \u00e2\u2020\u2019 **PRINT** progress \u00e2\u2020\u2019 user confirmation \u00e2\u2020\u2019 next file\n117|  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch \u00e2\u2020\u2019 **{BP}** web search for all files \u00e2\u2020\u2019 output web search results to chat \u00e2\u2020\u2019 document findings \u00e2\u2020\u2019 **PRINT** progress \u00e2\u2020\u2019 user confirmation \u00e2\u2020\u2019 next batch\n118|  - **Automatic**: For each file individually: **SCAN** \u00e2\u2020\u2019 **{BP}** web search \u00e2\u2020\u2019 output web search results to chat \u00e2\u2020\u2019 document findings \u00e2\u2020\u2019 **PRINT** progress \u00e2\u2020\u2019 next file (auto-stop on errors)\n119|  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch \u00e2\u2020\u2019 **{BP}** web search for all files \u00e2\u2020\u2019 output web search results to chat \u00e2\u2020\u2019 document findings \u00e2\u2020\u2019 **PRINT** progress \u00e2\u2020\u2019 next batch (auto-stop on errors)\n120|- 12. For each file, verify compliance criteria based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md as SSOT for detailed requirements\n121|- 13. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to report file\n122|- 14. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format using Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md as SSOT for prompting patterns\n123|- 15. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single file without exception\n124|- 16. **VALIDATION**: Validate that **{BP}** web search was performed for every single file without exception\n125|- 17. **VALIDATION**: Validate that findings were documented to report file after each file/batch scan\n126|- 18. **VALIDATION**: Validate that files were processed in alphabetical order\n127|- 19. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)\n128|- 20. **STATUS TRACKING**: Update workflow status to \"phase_5_complete\"\n129|- 21. **IF App Mode**: **PRINT** \"Compliance scanning complete - [N] files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT\"\n130|- 22. **IF Harness Mode**: **PRINT** \"Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT\"\n131|\n132|### Phase 6. Findings Consolidation (Scan Report Processing)\n133|- 1. Collect all scanning results from SCAN-REPORT file based on scanning mode:\n134|  - **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md\n135|  - **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md\n136|- 2. Consolidate findings by category and severity using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md severity classifications\n137|- 3. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file in SCAN-REPORT - no file may be left unexamined or unreported\n138|- 4. Cross-validate findings to eliminate duplicates and ensure consistency across all files\n139|- 5. **VALIDATION**: Validate that findings consolidation completed successfully for every single file\n140|- 6. **STATUS TRACKING**: Update workflow status to \"phase_6_complete\"\n141|- 7. **IF App Mode**: **PRINT** \"Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] files - every file examined\"\n142|- 8. **IF Harness Mode**: **PRINT** \"Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] governance files - every governance file examined\"\n143|\n144|### Phase 7. Compliance Report Generation\n145|- 1. Consolidate SCAN-REPORT to include comprehensive compliance analysis:\n146|  - Executive summary (overall compliance score, critical findings count, files examined)\n147|  - Detailed findings by file with line numbers and specific violations for each file\n148|  - Severity ratings with context for why each issue matters per file\n149|  - Actionable recommendations with clear improvement paths per file\n150|  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file\n151|- 2. **CRITICAL REQUIREMENT**: Ensure SCAN-REPORT includes analysis for every single file - no file may be omitted from the report\n152|- 3. **CRITICAL REQUIREMENT**: SCAN-REPORT is the single comprehensive report - no separate files needed\n153|- 4. **VALIDATION**: Validate that SCAN-REPORT consolidation completed successfully and every file is included\n154|- 5. **STATUS TRACKING**: Update workflow status to \"phase_7_complete\"\n155|- 6. **IF App Mode**: **PRINT** \"SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/App/ - includes detailed analysis for every single file\"\n156|- 7. **IF Harness Mode**: **PRINT** \"SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/Harness/ - includes detailed analysis for every single governance file\"\n157|\n158|### Phase 8. Final Validation + User Review\n159|- 1. Verify report completeness and accuracy\n160|- 2. Ensure all findings are properly documented with specific references\n161|- 3. Check that recommendations are actionable and clear\n162|- 4. **VALIDATION**: Validate that final validation completed successfully\n163|- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns\n164|- 6. **STATUS TRACKING**: Update workflow status to \"phase_8_complete\"\n165|- 7. **PRINT** \"Final validation complete - compliance report ready for user review\"\n166|\n167|### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)\n168|- 1. **PRINT** \"Best Practice Scanner workflow execution complete - workflow terminated\"\n169|- 2. **IF App Mode**: **PRINT** \"Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/App/ for review and action\"\n170|- 3. **IF Harness Mode**: **PRINT** \"Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/Harness/ for review and action\"\n171|- 4. **TERMINATE**: End workflow execution (do not return to step 1)\n172|\n173|---\n174|\n175|## Universal Framework References\n176|\n177|### Quality Assessment\n178|- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md\n179|- **Reviewer Customization**: Reviewer-specific quality criteria for compliance verification\n180|- **Focus**: Compliance quality assessment with governance verification\n181|\n182|### Validation Enforcement\n183|- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md\n184|- **Reviewer Customization**: Reviewer-specific validation patterns for scanning verification\n185|- **Focus**: Scanning validation and findings verification\n186|\n187|### Execution Strategy\n188|- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md\n189|- **Reviewer Customization**: Reviewer-specific execution patterns for large-scale scanning\n190|- **Focus**: Subagent coordination and failure handling during comprehensive scanning\n191|\n192|### State Management\n193|- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md\n194|- **Reviewer Customization**: Reviewer-specific state tracking for scanning progress\n195|- **Focus**: Scanning progress tracking and findings consolidation state management\n196|\n197|### Review Mode Patterns\n198|- **Reviewer-Specific Framework**: Workflow/Reviewer/Reference/Review_Mode_Patterns.md\n199|- **Reviewer Customization**: Reviewer-specific execution mode patterns for comprehensive code review\n200|- **Focus**: Step-by-step review oversight, file-by-file review patterns, subagent coordination\n201|\n202|## Subagent Prompting Strategy\n203|\n204|### Large-Scale Scanning Approach\n205|For large-scale scanning (>150 files), use parallel subagents by module/category following the prompting patterns and templates defined in Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (SSOT for subagent prompting).\n206|\n207|### Subagent Coordination\n208|- Launch 4-5 parallel subagents for independent module/categories\n209|- Each subagent receives precise scope with specific file list\n210|- Define exact output format for consistent consolidation\n211|- Validate subagent results against compliance standards\n212|- Consolidate findings into comprehensive report\n213|\n214|## Scan Complexity Assessment\n215|\n216|Based on scanning mode:\n217|- **App Mode**: 209 files expected (application code scanning)\n218|- **Harness Mode**: 173 files expected (governance files scanning)\n219|- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)\n220|- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module/category\n221|- **Estimated Duration**: Extended (mandatory **{BP}** web search for each file)\n222|- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per file)\n223|- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per file\n224|- **Process**: **SCAN** file (alphabetical order) \u00e2\u2020\u2019 **{BP}** web search \u00e2\u2020\u2019 **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) \u00e2\u2020\u2019 Next file (repeat for all files)\n225|- **Final Output**: Single comprehensive SCAN-REPORT containing all findings, analysis, and recommendations\n226|- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process\n227|\n228|## Execution Mode Recommendations\n229|\n230|- **Manual Mode**: Recommended for comprehensive scan to review each **{BP}** web search result and file analysis as it completes for maximum oversight\n231|- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 files at a time with confirmation between batches\n232|- **Automatic Batched Mode**: Maximum efficiency for large codebases - processes 5-10 files at a time automatically without confirmation\n233|\n234|**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each file undergoes: **SCAN** (line-by-line examination) \u00e2\u2020\u2019 **{BP}** (mandatory web search for current best practices) \u00e2\u2020\u2019 **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) \u00e2\u2020\u2019 Next file. The final SCAN-REPORT serves as the single comprehensive report containing all findings, analysis, and recommendations. This process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.\n235|\n236|## Context Management Strategy\n237|\n238|### PostCompaction Hook Configuration\n239|- **Hook File**: .devin/hooks.v1.json\n240|- **Purpose**: Reload governance files when context is compressed\n241|- **Configuration**: Ensure PostCompaction hook is configured to reload:\n242|  - Rules/Reviewer/Reviewer_Rules.md\n243|  - PRINCIPLES.md\n244|  - Workflow/Workflow_Reference/Terminology_Glossary.md\n</file-view>",
    "error": null
  },
  "session_id": "sphenoid-field",
  "prompt_id": "30058767-740d-4469-adef-2d6935c5bb8e"
}
```

---
