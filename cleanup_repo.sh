#!/bin/bash
# ===================================================================
# Repository Cleanup Script
# Removes files that should be in .gitignore
# ===================================================================

echo "🧹 Repository Cleanup Script"
echo "==========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to get directory size
get_size() {
    du -sh "$1" 2>/dev/null | cut -f1
}

# Function to count files
count_files() {
    find "$1" -type f 2>/dev/null | wc -l
}

echo "📊 Current Repository Status:"
echo "-------------------------------------------"

# Check sizes
if [ -d "myenv" ]; then
    VENV_SIZE=$(get_size "myenv")
    echo "Virtual Environment (myenv/): $VENV_SIZE"
fi

if [ -d "chroma_db" ]; then
    CHROMA_SIZE=$(get_size "chroma_db")
    echo "ChromaDB (chroma_db/): $CHROMA_SIZE"
fi

if [ -d "tests/chroma_db" ]; then
    TEST_CHROMA_SIZE=$(get_size "tests/chroma_db")
    echo "Test ChromaDB (tests/chroma_db/): $TEST_CHROMA_SIZE"
fi

# Count cache files
CACHE_COUNT=$(find . -name "*.pyc" -o -name "*.pyo" -o -name "__pycache__" | wc -l)
echo "Python cache files: $CACHE_COUNT"

# Count log files
LOG_COUNT=$(find . -name "*.log" | wc -l)
echo "Log files: $LOG_COUNT"

echo ""
echo "-------------------------------------------"
echo ""

# Ask for confirmation
read -p "Do you want to clean these files? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo ""
echo "🧹 Starting cleanup..."
echo ""

# 1. Remove Python cache files
echo "1️⃣  Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "   ✅ Python cache cleaned"

# 2. Remove log files
echo "2️⃣  Removing log files..."
find . -type f -name "*.log" -delete 2>/dev/null
echo "   ✅ Log files removed"

# 3. Remove build artifacts
echo "3️⃣  Removing build artifacts..."
rm -rf build/ dist/ *.egg-info/ .eggs/ 2>/dev/null
echo "   ✅ Build artifacts removed"

# 4. Remove pytest cache
echo "4️⃣  Removing test cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
rm -rf .coverage htmlcov/ .nyc_output/ 2>/dev/null
echo "   ✅ Test cache cleaned"

# 5. Remove temp files
echo "5️⃣  Removing temporary files..."
find . -type f \( -name "*.tmp" -o -name "*.temp" -o -name "*.bak" -o -name "*.backup" \) -delete 2>/dev/null
echo "   ✅ Temporary files removed"

# 6. Remove OS-specific files
echo "6️⃣  Removing OS-specific files..."
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null
echo "   ✅ OS files removed"

# 7. Remove editor files
echo "7️⃣  Removing editor backup files..."
find . -name "*~" -delete 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null
echo "   ✅ Editor backups removed"

echo ""
echo "-------------------------------------------"
echo "✅ Cleanup complete!"
echo ""

# Show new status
echo "📊 After Cleanup:"
echo "-------------------------------------------"

CACHE_COUNT_AFTER=$(find . -name "*.pyc" -o -name "*.pyo" -o -name "__pycache__" | wc -l)
LOG_COUNT_AFTER=$(find . -name "*.log" | wc -l)

echo "Python cache files: $CACHE_COUNT_AFTER (was $CACHE_COUNT)"
echo "Log files: $LOG_COUNT_AFTER (was $LOG_COUNT)"

echo ""
echo "💡 Note: Large directories not removed:"
if [ -d "myenv" ]; then
    echo "   • myenv/ ($VENV_SIZE) - Virtual environment"
fi
if [ -d "chroma_db" ]; then
    echo "   • chroma_db/ ($CHROMA_SIZE) - Vector database"
fi
if [ -d "node_modules" ]; then
    NODE_SIZE=$(get_size "node_modules")
    echo "   • node_modules/ ($NODE_SIZE) - Node packages"
fi

echo ""
echo "🔒 These are already in .gitignore and won't be committed."
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git status"
echo "   2. Remove tracked ignored files: git rm --cached <file>"
echo "   3. Commit: git commit -m 'Clean up repository'"
echo ""
