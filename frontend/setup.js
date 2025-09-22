#!/usr/bin/env node
/**
 * Setup script for Vietnamese AI Dubbing Frontend
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runCommand(command, description) {
  console.log(`🔧 ${description}`);
  try {
    const result = execSync(command, { encoding: 'utf8' });
    console.log(`✅ ${description} completed successfully`);
    return true;
  } catch (error) {
    console.error(`❌ ${description} failed:`);
    console.error(error.stdout || error.message);
    return false;
  }
}

function main() {
  console.log('🚀 Setting up Vietnamese AI Dubbing Frontend');
  console.log('='.repeat(50));

  // Check Node.js version
  const nodeVersion = process.version;
  console.log(`✅ Node.js ${nodeVersion}`);

  // Check if package.json exists
  if (!fs.existsSync('package.json')) {
    console.error('❌ package.json not found. Please run this script from the frontend directory.');
    process.exit(1);
  }

  // Install dependencies
  if (!runCommand('npm install', 'Install Node.js dependencies')) {
    process.exit(1);
  }

  // Check if .env file exists, create if not
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) {
    console.log('📝 Creating .env file...');
    const envContent = `# Vietnamese AI Dubbing Frontend Configuration
VITE_API_URL=http://localhost:8000/api/v1

# Add other environment variables as needed
`;
    fs.writeFileSync(envPath, envContent);
    console.log('✅ .env file created');
  }

  // Run type checking
  console.log('🧪 Running type checking...');
  try {
    execSync('npx tsc --noEmit', { stdio: 'inherit' });
    console.log('✅ TypeScript type checking passed');
  } catch (error) {
    console.log('⚠️  TypeScript type checking found some issues, but continuing...');
  }

  console.log('\n' + '='.repeat(50));
  console.log('🎉 Frontend setup completed successfully!');
  console.log('📝 To start the frontend development server:');
  console.log('   npm run dev');
  console.log('🌐 Frontend will be available at: http://localhost:5173');
  console.log('='.repeat(50));
}

main();