# Refactoring Agent Context & Instructions

**Senior AWS Solutions Architect** | **Language:** English Only  
**Purpose:** Agent guidance system for principle-driven BuildingOS refactoring  
**Methodology:** 9 Fundamental Principles execution framework  
**Last Updated:** 2025-01-11

---

## 🚨 **CRITICAL: AGENT EXECUTION PROTOCOL**

### **🎯 PRIMARY GUIDANCE SOURCE**
**MANDATORY:** Always consult `docs/03-development/01-project-management/backlog.md` for current priorities and work assignments.

**NEVER work from deprecated sources:**
- ❌ `refactoring-checklist.md` (DEPRECATED - archived in legacy)
- ❌ Old task lists or outdated documentation
- ❌ Assumptions about work priorities

---

## 📚 **MANDATORY READING SEQUENCE**

### **🔍 Before Starting ANY Refactoring Work:**

1. **FIRST:** Read `docs/03-development/01-project-management/refactoring-principles.md`
   - **Purpose:** Complete methodology understanding
   - **Requirement:** MUST understand all 9 principles before proceeding
   - **Critical:** No work can begin without this foundational knowledge

2. **SECOND:** Check `docs/03-development/01-project-management/backlog.md`
   - **Purpose:** Identify current priorities and epic assignments
   - **Focus:** Find the highest priority epic that is "READY TO START"
   - **Dependencies:** Verify all prerequisites are met before beginning

3. **THIRD:** Review `docs/03-development/01-project-management/current-sprint.md`
   - **Purpose:** Understand current sprint context and progress
   - **Update:** Mark your principle progress as you work
   - **Coordination:** Ensure no conflicts with other team members

---

## 🎯 **STEP EXECUTION PROTOCOL**

### **📋 The 9 Principles Framework**
Every epic MUST follow this exact sequence:

#### **Phase 1: Analysis & Planning** 🔍
1. **READ PRINCIPLES:** Complete review of refactoring-principles.md
2. **EXECUTE PRINCIPLE 1:** Global Analysis Requirements
   - Start from global `building-os-platform` directory analysis
   - Map all dependencies across entire project structure
   - Validate prerequisites and integration points
3. **EXECUTE PRINCIPLE 8:** Dependency Validation Framework
   - Confirm all upstream dependencies are operational
   - Test integration points and communication channels
4. **DOCUMENT:** Analysis results and implementation plan

#### **Phase 2: Design & Approval** 📋
1. **DESIGN:** Create comprehensive implementation plan
2. **EXECUTE PRINCIPLE 5:** Get design approval before proceeding
   - Present architecture design and benefits
   - Explain integration patterns and optimizations
   - Get explicit approval to proceed to build phase
3. **VALIDATE:** All stakeholders approve proposed changes
4. **DOCUMENT:** Approved design and implementation strategy

#### **Phase 3: Implementation** 🏗️
1. **EXECUTE PRINCIPLE 2:** Clean Build Standards
   - Follow AWS and Terraform best practices
   - Use global modules consistently
   - Implement VPC integration and security best practices
2. **EXECUTE PRINCIPLE 3:** Testing & Validation Framework
   - Create comprehensive validation scripts
   - Test all resources and integrations
   - Validate performance and security
3. **EXECUTE PRINCIPLE 4:** Documentation Standards
   - Add comprehensive English file headers
   - Document all code blocks with detailed comments
   - Ensure no non-English text remains
4. **VALIDATE:** All quality gates passed

#### **Phase 4: Validation & Integration** 🧪
1. **INTEGRATE:** Complete integration testing
2. **EXECUTE PRINCIPLE 9:** Quality Gates Enforcement
   - Validate all automated quality checks passing
   - Confirm architecture compliance
   - Verify testing requirements met
3. **VALIDATE:** All systems operational and integrated
4. **DOCUMENT:** Integration results and performance metrics

#### **Phase 5: Documentation & Project Management** 📊
1. **EXECUTE PRINCIPLE 6:** Project Management Update Protocol
   - Update `current-sprint.md` with principle completion
   - Update `backlog.md` epic status
   - Add completion to `completed.md`
   - Update `metrics.md` with achievements
2. **EXECUTE PRINCIPLE 7:** Infrastructure Documentation Update Protocol
   - Update `solution-architecture.md` with comprehensive details
   - Create/update relevant ADRs
   - Update component documentation
   - Document monitoring and operations procedures
3. **EXECUTE PRINCIPLE 5:** Final approval and sign-off
4. **COMPLETE:** Mark epic as completed in project management system

---

## 📊 **PROJECT MANAGEMENT INTEGRATION**

### **🔄 Continuous Updates Required**
As you execute each principle, you MUST update project management files:

#### **📈 Current Sprint Updates:**
- **File:** `docs/03-development/01-project-management/current-sprint.md`
- **Frequency:** After completing each principle
- **Content:** Mark principle completion with timestamps and notes
- **Format:** Update the principle completion checklist

#### **📋 Backlog Status:**
- **File:** `docs/03-development/01-project-management/backlog.md`
- **Frequency:** When epic status changes
- **Content:** Update epic status (In Progress → Review → Completed)
- **Dependencies:** Update dependency status for downstream epics

#### **✅ Completed Work Tracking:**
- **File:** `docs/03-development/01-project-management/completed.md`
- **Frequency:** When epic is fully completed
- **Content:** Add comprehensive completion record with:
  - All principle completion details
  - Quality metrics achieved
  - Lessons learned and best practices
  - Technical achievements and improvements

#### **📊 Metrics Updates:**
- **File:** `docs/03-development/01-project-management/metrics.md`
- **Frequency:** Weekly or at epic completion
- **Content:** Update quality metrics, performance data, cost optimizations

---

## 🎯 **QUALITY GATES & VALIDATION**

### **🔒 Mandatory Quality Checks**
Before marking any principle as complete:

#### **Principle 1 - Global Analysis:**
- [ ] Complete dependency map created and validated
- [ ] All integration points identified and documented
- [ ] Impact assessment completed with risk mitigation plans
- [ ] Analysis results reviewed and approved

#### **Principle 2 - Clean Build:**
- [ ] All resources follow global module patterns
- [ ] Security best practices implemented and validated
- [ ] Performance optimization strategies applied
- [ ] Code quality standards met (headers, comments, naming)

#### **Principle 3 - Testing & Validation:**
- [ ] All validation scripts pass with 100% success rate
- [ ] Infrastructure tests demonstrate proper functionality
- [ ] Application flows work end-to-end
- [ ] Monitoring and alerting systems operational

#### **Principle 4 - Documentation:**
- [ ] All files have comprehensive English headers
- [ ] All code blocks have detailed English comments
- [ ] Variable and output descriptions are complete
- [ ] No non-English text remains in code or documentation

#### **Principle 5 - Approval Gates:**
- [ ] Design approved by team before implementation
- [ ] Code review completed with all feedback addressed
- [ ] All tests passing and validation complete
- [ ] Final approval received to proceed

#### **Principle 6 - Project Management:**
- [ ] Current sprint status updated with accurate progress
- [ ] Backlog reflects current priorities and dependencies
- [ ] Completed work properly documented with metrics
- [ ] All project management files synchronized

#### **Principle 7 - Infrastructure Documentation:**
- [ ] Solution architecture document comprehensively updated
- [ ] All architectural decisions documented in ADRs
- [ ] Component documentation reflects current implementation
- [ ] Monitoring and operations documentation current

#### **Principle 8 - Dependency Validation:**
- [ ] All prerequisites validated and operational
- [ ] Integration testing completed successfully
- [ ] Dependency documentation updated
- [ ] Rollback procedures tested and documented

#### **Principle 9 - Quality Gates:**
- [ ] All automated quality checks passing
- [ ] Architecture review completed and approved
- [ ] Documentation standards verified and complete
- [ ] Testing requirements met with full validation

---

## 🚨 **CRITICAL ERROR PREVENTION**

### **❌ Common Mistakes to Avoid:**

1. **Skipping Principles:** NEVER skip or partially complete principles
2. **Working from Old Sources:** NEVER use deprecated checklist or old task lists
3. **Incomplete Documentation:** NEVER leave documentation updates for later
4. **Missing Approvals:** NEVER proceed without explicit approval gates
5. **Inadequate Testing:** NEVER skip validation scripts or quality checks

### **✅ Success Patterns to Follow:**

1. **Read First:** Always start by reading principles document completely
2. **Follow Sequence:** Execute all 9 principles in exact order
3. **Update Continuously:** Keep project management files current
4. **Validate Thoroughly:** Ensure all quality gates pass before proceeding
5. **Document Comprehensively:** Maintain excellent English documentation throughout

---

## 📋 **KEY FILES TO MONITOR**

### **📊 Daily Monitoring:**
- **Current priorities:** `backlog.md` - Check for priority changes
- **Sprint progress:** `current-sprint.md` - Update principle completion
- **Team coordination:** Communicate with team on shared resources

### **📈 Weekly Reviews:**
- **Completed work:** `completed.md` - Review lessons learned
- **Quality metrics:** `metrics.md` - Assess performance trends
- **Process improvements:** Identify optimization opportunities

### **🏛️ Architecture References:**
- **Best practices:** `docs/02-architecture/01-solution-architecture/architecture-best-practices-checklist.md`
- **Current architecture:** `docs/02-architecture/01-solution-architecture/solution-architecture.md`
- **Decision records:** `docs/02-architecture/02-adr/` - Review relevant ADRs

---

## 🎯 **SUCCESS CRITERIA FOR AGENTS**

### **📊 Epic Completion Requirements:**
- ✅ All 9 principles completed in sequence
- ✅ All quality gates passed
- ✅ All validation scripts passing
- ✅ Project management files updated
- ✅ Infrastructure documentation current
- ✅ Team approval received

### **🚀 Quality Standards Achievement:**
- ✅ 100% English documentation coverage
- ✅ Comprehensive file headers and code comments
- ✅ Architecture best practices followed
- ✅ All dependencies validated and operational
- ✅ Performance and cost optimization achieved

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **📈 Learning & Adaptation:**
- **Document Lessons:** Record insights and improvements in completed.md
- **Share Knowledge:** Communicate best practices with team
- **Process Feedback:** Suggest improvements to principles framework
- **Quality Evolution:** Continuously improve validation and quality standards

### **🎯 Agent Development:**
- **Skill Building:** Develop expertise in AWS and Terraform best practices
- **Methodology Mastery:** Become proficient in 9 principles execution
- **Quality Focus:** Maintain high standards for documentation and validation
- **Team Collaboration:** Work effectively within principle-driven framework

---

**Navigation:**
📋 Work Source: [Development Backlog](../03-development/01-project-management/backlog.md)  
📚 Methodology: [Refactoring Principles](../03-development/01-project-management/refactoring-principles.md)  
📊 Progress Tracking: [Current Sprint](../03-development/01-project-management/current-sprint.md)  
✅ Completion Records: [Completed Work](../03-development/01-project-management/completed.md)  
🏠 Home: [Documentation Index](../README.md)

---

**Status:** 🚀 **AGENT GUIDANCE SYSTEM OPERATIONAL**  
**Usage:** Follow this guide for all BuildingOS refactoring work  
**Quality Assurance:** All 9 principles must be completed for every epic  
**Success Criteria:** Epic completion with full validation and team approval
