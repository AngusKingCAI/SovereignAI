# Daytona Homepage

**Source URL:** https://www.daytona.io/

# Run AI Code.
Secure and Elastic Infrastructure for Running Your AI-Generated Code.

## Start for Free
Python, TypeScript, Ruby, Go, Java - `pip install daytona`

```python
from daytona import Daytona

daytona = Daytona()
sandbox = daytona.create()
response = sandbox.process.exec("echo 'Hello, World!'")
print(response.result)
sandbox.delete()
```

## Companies Using Daytona
Agents at these companies use Daytona:
- LangChain
- AfterQuery
- Mintlify
- SambaNova
- Mastra
- n8n
- Clay
- Parabola

## Fast, Scalable, Stateful Infrastructure for AI Agents

### Lightning-Fast Infrastructure for AI Development
- **Sub 90ms** sandbox creation from code to execution
- **Separated & Isolated Runtime Protection** - Execute AI-generated code with zero risk to your infrastructure
- **Massive Parallelization** for Concurrent AI Workflows - Execute code in isolated environments with realtime output

## Programmatic Control
File, Git, LSP, and Execute API

### Process Execution
Execute code and commands in isolated envs with real-time output streaming.

### File System Operations
Manage sandboxes with full CRUD operations and granular permission controls.

### Git Integration
Native Git operations and secure credential handling.

### Builtin LSP Support
Language server features with multi-language completion and real-time analysis.

```python
from daytona import Daytona, CreateSandboxParams

daytona = Daytona()

params = CreateSandboxParams(
    language="python",
)
sandbox = daytona.create(params)

# Run the code securely inside the sandbox
response = sandbox.process.code_run('print("Hello World!")')
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

# Execute an os command in the sandbox
response = sandbox.process.exec('echo "Hello World from exec!"', cwd="/home/daytona", timeout=10)
if response.exit_code != 0:
    print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)

daytona.remove(sandbox)
```

## AI-First Infrastructure
Optimized for LLMs, Agents, and Evals

- **AI Evaluations** - Scale evals across parallel environments with reproducible snapshot states
- **Code Interpreter** - Run untrusted code in isolated environments with real-time output streaming
- **Coding Agents** - Execute AI agents code with RESTful API and state persistence across parallel runs
- **Data Analysis** - Process large datasets on clusters with optimized data locality
- **Data Visualisation** - Enable your AI agent to run code and instantly render charts, plots, and visual outputs
- **Reinforcement Learning for Agents** - Simplify RL training and enable long-horizon planning in dynamic, stateful environments
- **Computer Use** - Let Your Agent Use the Computer Like a Human Would

## More Than a Sandbox
The Runtime AI Agents Actually Need

### Environment Snapshots
Save, Restore, and Resume Any Agent Workflow Instantly

### Run Near Your Agents
Low-Latency Sandboxes Deployed in Your Region
- India Asia-South
- EU Central (Frankfurt)
- EU West (London)
- US East (Washington DC)
- US West (Oregon)

### Stateful by Design
Daytona Sandboxes Run Indefinitely — Built for Long-Running Tasks and Persistent Agents

### Volumes
Let Agents Access Shared Data Across Sandboxes Without Breaking Isolation

## Computer Use
Secure virtual desktops (Linux, Windows, macOS) you can control with code. Deploy desktop automation with full programmatic access and isolated environments.

### Linux (Ubuntu)
Linux desktop with full root access. Ready for automation, development, and testing with complete programmatic control.

### MacOS
macOS desktop for iOS development and testing. Code-controlled macOS instances perfect for mobile app automation and development.

### Windows
Full Windows desktop with programmatic control. Perfect for Windows-specific automation, testing, and development workflows.

## Human in the Loop
Full Access for Debugging, Oversight, or Intervention—Without Breaking Autonomy

### SSH Access
Secure Shell Access to Any Sandbox, Instantly and Safely

### VS Code Browser
Open Sandboxes in Your Editor With One Click

### Web Terminal
Full Terminal in the Browser. No Setup. No Latency.

## Trust Through Transparency
Open Codebase. Your Cloud. Certified Security.

### Open-Source Transparency
Verify Every Line of Code. No Black Boxes. No Hidden Logic.

### Customer-Managed Compute
Sandboxes run on isolated, customer-managed compute in your cloud. Daytona provides the control plane. No shared compute. No cross-tenant risk.

### Enterprise Compliance
Meets HIPAA, SOC 2, and GDPR Standards Out of the Box.

## Instant Sandboxes. Pay-as-You-Go.
Daytona lets you spin up sandboxes in milliseconds and shut them down just as fast. Use what you need, when you need it. $200 in free compute included.

## What Builders Say About Daytona

### Abhi Ingle, Chief Product & Strategy Officer at SambaNova
"One thing that Daytona does incredibly well is its sandbox provisioning times. When you're provisioning tens of thousands of sandboxes, those milliseconds add up, and no other solution we tested could match their speed."

### Harrison Chase, CEO & Founder of LangChain
"While building our coding agent, we hit limitations around our sandboxing. Daytona jumped in, contributed a working PR within hours, and fully unblocked us. They pulled a Collison."

### Paul van der Boor, Vice President of AI at Prosus
"Maintaining a homegrown sandbox solution that powers apps for billions of global users was expensive and time-consuming. We didn't have the bandwidth to upgrade it because we wanted to move forward with our actual AI products."

### Jernej Strasner, Director of Engineering at Sentry
"Provisioning development environments remains to be a pain. Existing solutions focus too much on remote environments somewhere in 'the cloud'. Daytona's approach is much smarter – help the developer in any environment, remote or local."

### Shawn Wang, Writer, Speaker, Developer Advocate
"At last, we can standardize development environments to function more like a well-oiled machine than bespoke artworks. This lets devs spin up and shut down environments seamlessly, avoiding configuration drift."

### Brian Douglas, Founder and CEO, Open Sauced
"The industry has chosen the cloud as the premier place to distribute software, but space for building software is wide open. Daytona is uniquely positioned to own this space and I want to be a part of that revolution."

## Docker Integration
Agents can now use the same tools as humans. Everything Docker Provides Natively Now as Part of Daytona.

### Declarative Image Builder
Build Snapshots Through the SDK. No CLI. No Uploads. No Registry.

### Image Templates Based on Docker
Use Off-the-Shelf Docker Images Without Modification or Wrappers.

### Docker in Docker
Easily Run Docker Containers Inside Daytona Sandboxes.

### Dockerfile Support
Drop in a Dockerfile and Daytona Handles the Rest.

### Docker Compose Support
With Daytona, Agents Also Get Ready-to-Code Environments From a Single File

## FAQs
Extra questions about the how and the why? Reach out on our community channel and we'll happily expand.

- What is Daytona and how does it enable AI?
- How does Daytona ensure the safe execution of AI-generated code?
- What are AI Sandboxes and how do they enhance agentic AI workflows?
- How can I integrate Daytona into my existing development stack?
- What security measures does Daytona implement for AI development?
- Can I Run My Own Instance of Daytona?

## Additional Resources
- Subscribe to DotFiles Insider newsletter
- Startup Program
- Documentation
- Contact
- Blog
- Pricing
- System Status
- Changelog
- Trust Center

This is the official Daytona homepage, providing secure and elastic infrastructure for running AI-generated code with lightning-fast sandbox creation, stateful operations, and enterprise-grade security.
