import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Search for Python imports and dependencies",
  args: {
    pattern: tool.schema.string().describe("Search pattern (e.g., 'telegram', 'asyncio')"),
  },
  async execute(args, context) {
    const dir = context.worktree
    
    // Search for imports
    const imports = await Bun.$`grep -r "import ${args.pattern}" ${dir} --include="*.py" | head -20`.text()
    
    // Search for from imports
    const fromImports = await Bun.$`grep -r "from ${args.pattern}" ${dir} --include="*.py" | head -20`.text()
    
    // Search in requirements
    const requirements = await Bun.$`grep -i "${args.pattern}" ${dir}/requirements*.txt 2>/dev/null || echo "Not found in requirements"`.text()
    
    return `
Imports for '${args.pattern}':
${imports || "No imports found"}

From imports:
${fromImports || "No from imports found"}

Requirements:
${requirements}
    `.trim()
  },
})
