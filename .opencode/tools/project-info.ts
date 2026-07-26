import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Get project information and statistics",
  args: {},
  async execute(args, context) {
    const dir = context.worktree
    
    // Count files
    const pyFiles = await Bun.$`find ${dir} -name "*.py" -type f | wc -l`.text()
    const mdFiles = await Bun.$`find ${dir} -name "*.md" -type f | wc -l`.text()
    
    // Get git info
    let gitInfo = "Not a git repo"
    try {
      const branch = await Bun.$`git -C ${dir} branch --show-current`.text()
      const commits = await Bun.$`git -C ${dir} rev-list --count HEAD`.text()
      gitInfo = `Branch: ${branch.trim()}, Commits: ${commits.trim()}`
    } catch {}
    
    // Get directory structure
    const structure = await Bun.$`ls -la ${dir}`.text()
    
    return `
Project Statistics:
- Python files: ${pyFiles.trim()}
- Markdown files: ${mdFiles.trim()}
- Git: ${gitInfo}

Directory Structure:
${structure}
    `.trim()
  },
})
