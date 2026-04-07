#!/usr/bin/env node

import { existsSync } from 'node:fs';
import { mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';

const DEFAULT_BRANCH = 'master';
const DEFAULT_REPO = process.env.SKILLS_REPO || 'https://github.com/your-org/skills.git';

const run = (cmd, args, cwd) => new Promise((resolve, reject) => {
  const child = spawn(cmd, args, {
    cwd,
    stdio: 'inherit',
    shell: process.platform === 'win32'
  });
  child.on('close', (code) => {
    if (code === 0) {
      resolve();
      return;
    }
    reject(new Error(`命令失败: ${cmd} ${args.join(' ')}`));
  });
  child.on('error', reject);
});

const parseOptions = (args) => {
  const options = {
    branch: DEFAULT_BRANCH,
    repo: DEFAULT_REPO
  };

  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (token === '--branch') {
      options.branch = args[i + 1] || DEFAULT_BRANCH;
      i += 1;
      continue;
    }
    if (token === '--repo') {
      options.repo = args[i + 1] || DEFAULT_REPO;
      i += 1;
      continue;
    }
  }

  return options;
};

const updateSkills = async (options) => {
  const codexHome = process.env.CODEX_HOME || path.join(homedir(), '.codex');
  const targetDir = path.join(codexHome, 'skills');
  const gitDir = path.join(targetDir, '.git');

  await mkdir(codexHome, { recursive: true });

  if (!existsSync(targetDir)) {
    console.log(`未检测到技能目录，开始克隆: ${targetDir}`);
    await run('git', ['clone', '--branch', options.branch, '--depth', '1', options.repo, targetDir]);
    console.log('技能安装完成。');
    return;
  }

  if (!existsSync(gitDir)) {
    throw new Error(`目录已存在但不是 Git 仓库: ${targetDir}`);
  }

  console.log(`开始更新技能目录: ${targetDir}`);
  await run('git', ['fetch', 'origin', options.branch], targetDir);
  await run('git', ['checkout', options.branch], targetDir);
  await run('git', ['pull', '--ff-only', 'origin', options.branch], targetDir);
  console.log('技能更新完成。');
};

const printHelp = () => {
  console.log(`skills 命令用法:

  npx skills update [--branch master] [--repo <git_url>]

说明:
  update    拉取指定分支并更新到 $CODEX_HOME/skills（默认 ~/.codex/skills）

环境变量:
  CODEX_HOME  指定 Codex 工作目录
  SKILLS_REPO 指定默认技能仓库地址
`);
};

const main = async () => {
  const [, , command, ...rest] = process.argv;

  if (!command || command === '-h' || command === '--help') {
    printHelp();
    return;
  }

  if (command === 'update') {
    const options = parseOptions(rest);
    await updateSkills(options);
    return;
  }

  throw new Error(`未知命令: ${command}`);
};

main().catch((error) => {
  console.error(`\n[skills] ${error.message}`);
  process.exit(1);
});
