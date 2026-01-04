# Showcase AI Agents System Documentation

## 📋 Overview

The **agents** folder is the AI brain of the Showcase application. It transforms raw resume data into beautiful, personalized portfolio websites using a multi-agent AI pipeline powered by Google Gemini.

**NOTE: ALL CODE IN THIS FOLDER IS AI GENERATED**

---

## 🎯 What This System Does

### Input (What Comes In)
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "skills": ["Python", "React", "ML"],
  "projects": [{
    "title": "AI Chatbot",
    "description": "Built a chatbot...",
    "technologies": ["Python", "TensorFlow"]
  }]
}
```

### Output (What Goes Out)
```json
{
  "hero": {
    "name": "John Doe",
    "tagline": "Building intelligent systems that solve real problems"
  },
  "bio": "I'm a machine learning engineer passionate about...",
  "projects": [{
    "title": "AI Chatbot",
    "description": "Developed an intelligent conversational AI system that...",
    "tech_stack": ["Python", "TensorFlow"],
    "featured": true
  }],
  "skills": {
    "languages": ["Python"],
    "frameworks": ["React", "TensorFlow"]
  },
  "theme": {
    "primary_color": "#4A90E2",
    "style": "modern_tech"
  }
}
```

---

## 🏗️ Architecture

### The Pipeline Flow

```
Raw Resume Data
      ↓
[1. Data Preprocessor] ← Cleans & validates data
      ↓
[2. Schema Builder] ← Analyzes & structures data
      ↓
[3. Content Generator] ← AI writes content (Gemini)
      ↓
[4. Validator] ← Quality checks
      ↓
Complete Portfolio
```

### Agent Hierarchy

```
agents/
├── orchestrator.py          # 🎭 Conductor - coordinates everything
├── core/
│   └── schema_builder.py    # 🏗️ Architect - designs structure
├── middleware/
│   └── data_preprocessor.py # 🧹 Janitor - cleans data
├── generation/
│   └── content_generator.py # ✨ Writer - creates content (AI)
├── validation/
│   └── validator.py         # ✅ Editor - quality control
└── integration.py           # 🔌 API - main entry point
```

---

## 📁 File-by-File Breakdown

### 1️⃣ `integration.py` - Main API Entry Point

**Purpose**: This is what your backend calls. Simple, clean API.

**Key Functions**:
```python
# Generate complete portfolio
portfolio = await generate_portfolio(parsed_data)

# Regenerate specific section
updated = await regenerate_section(portfolio, 'hero', preferences)

# Export to different formats
json_str = await export_portfolio(portfolio, 'json')
```

**Data Flow**:
- **IN**: Parsed resume data (from OCR + NLP)
- **OUT**: Complete portfolio configuration

---

### 2️⃣ `orchestrator.py` - The Conductor

**Purpose**: Coordinates all agents, manages the pipeline, handles errors.

**What It Does**:
1. Receives parsed resume data
2. Calls preprocessor to clean data
3. Calls schema builder to structure data
4. Calls content generator to create content
5. Calls validator to ensure quality
6. Returns complete portfolio

**Key Method**:
```python
async def process_resume(parsed_data):
    # 1. Clean data
    preprocessed = await preprocessor.preprocess(parsed_data)
    
    # 2. Build structure
    schema = await schema_builder.build_schema(preprocessed)
    
    # 3. Generate content
    content = await content_generator.generate(schema, preprocessed)
    
    # 4. Validate quality
    validated = await validator.validate_and_enhance(content)
    
    return validated
```

**Data Transformations**:
- **IN**: Raw parsed data
- **STEP 1**: Clean data
- **STEP 2**: Structured schema
- **STEP 3**: AI-generated content
- **STEP 4**: Validated portfolio
- **OUT**: Final portfolio

---

### 3️⃣ `middleware/data_preprocessor.py` - The Data Janitor

**Purpose**: Cleans messy input data before processing.

**What It Fixes**:
- ❌ `"   John   Doe   "` → ✅ `"John Doe"`
- ❌ `"john@invalid"` → ✅ `None` (invalid email)
- ❌ `["Python", "python", "PYTHON"]` → ✅ `["Python"]` (dedupe)
- ❌ `"github.com/user"` → ✅ `"https://github.com/user"`

**Data Quality Score**:
Calculates 0.0-1.0 score based on:
- Name present (10 points)
- Email valid (10 points)
- Skills listed (20 points)
- Projects described (30 points)
- Experience included (15 points)
- Education listed (10 points)
- Links provided (5 points)

**Example**:
```python
# BEFORE preprocessing
{
  "name": "  JOHN DOE  ",
  "email": "invalid-email",
  "skills": ["Python", "python", "js"]
}

# AFTER preprocessing
{
  "name": "John Doe",
  "email": None,  # Invalid, removed
  "skills": ["Python", "JavaScript"],  # Dedupe + normalize
  "metadata": {
    "data_quality_score": 0.65
  }
}
```

---

### 4️⃣ `core/schema_builder.py` - The Architect

**Purpose**: Analyzes data and creates blueprint for content generation.

**Key Responsibilities**:

1. **Detect Domain**: Determines user's profession
   - `ml_engineer`, `data_scientist`, `fullstack_developer`, etc.

2. **Categorize Skills**: Groups skills logically
   ```python
   {
     "languages": ["Python", "JavaScript"],
     "frameworks": ["React", "TensorFlow"],
     "tools": ["Docker", "AWS"]
   }
   ```

3. **Create Templates**: Blueprints for content generation
   ```python
   {
     "hero": {
       "template": "Building intelligent systems with {tech}",
       "needs_generation": True
     },
     "bio": {
       "structure": ["hook", "background", "expertise", "passion"],
       "tone": "professional_friendly"
     }
   }
   ```

4. **Layout Hints**: Tells frontend what to emphasize
   ```python
   {
     "emphasis": {
       "projects": "high",  # Show projects prominently
       "technical_depth": "high"
     }
   }
   ```

**Domain Detection Logic**:
```python
# Analyzes skills/projects for keywords
ml_keywords = ['machine learning', 'tensorflow', 'nlp']
frontend_keywords = ['react', 'vue', 'css']

# Scores each domain
if ml_score > 3: return 'ml_engineer'
if frontend_score + backend_score > 4: return 'fullstack_developer'
```

---

### 5️⃣ `generation/content_generator.py` - The AI Writer (Gemini)

**Purpose**: Uses Google Gemini to generate compelling content.

**What It Generates**:

1. **Hero Tagline** (8-15 words)
   ```python
   # Template: "Building intelligent systems with ML"
   # Generated: "Crafting AI solutions that transform healthcare"
   ```

2. **Professional Bio** (150-200 words)
   - Hook: Engaging introduction
   - Background: Career journey
   - Expertise: What you're great at
   - Passion: What drives you
   - Current focus: What you're doing now

3. **Enhanced Project Descriptions**
   - Takes: "Built a chatbot"
   - Creates: "Developed an intelligent conversational AI system using TensorFlow and NLP that reduced customer support response time by 40%"

**Constrained Generation**:
```python
prompt = f"""
Generate a hero tagline for a {domain}.

Context:
- Skills: {skills}
- Projects: {projects}

Requirements:
- 8-15 words maximum
- Action-oriented
- No clichés

Return ONLY the tagline.
"""

response = gemini.generate(prompt)
```

**Configuration**:
- Temperature: 0.7 (balanced creativity)
- Max tokens: 2048
- Model: gemini-pro

---

### 6️⃣ `validation/validator.py` - The Quality Editor

**Purpose**: Ensures generated content meets quality standards.

**Validation Checks**:

1. **Length Requirements**
   - Tagline: 5-20 words
   - Bio: 100-300 words
   - Project description: 30+ words

2. **No Placeholders**
   - ❌ `[placeholder text]`
   - ❌ `TODO: fill this`
   - ❌ `Lorem ipsum`

3. **Consistency**
   - Name matches across sections
   - Skills mentioned exist in original data
   - Project count is reasonable

4. **Tone & Voice**
   - Bio is first person ("I am" not "they are")
   - Professional but friendly
   - No repetitive patterns

**Quality Scoring**:
```python
overall_score = (
    hero_score * 0.25 +
    bio_score * 0.35 +
    projects_score * 0.40
)

# If score < 0.7: enhance or regenerate
```

**Example Issues Detected**:
```python
{
  "hero": {
    "score": 0.8,
    "issues": ["Tagline slightly long"]
  },
  "bio": {
    "score": 0.6,
    "issues": ["Too short", "Contains placeholder"],
    "passed": False
  }
}
```

---

## 🔄 Complete Data Flow Example

### Step-by-Step Transformation

#### 🔹 Step 0: Input (From OCR + NLP)
```json
{
  "name": "Alice Chen",
  "skills": ["python", "ml", "react", "tensorflow"],
  "projects": [{
    "title": "Chatbot",
    "description": "Made a bot"
  }]
}
```

#### 🔹 Step 1: After Preprocessing
```json
{
  "name": "Alice Chen",
  "email": null,
  "skills": ["Python", "Machine Learning", "React", "TensorFlow"],
  "projects": [{
    "title": "Chatbot",
    "description": "Made a bot",
    "technologies": [],
    "featured": true
  }],
  "metadata": {"data_quality_score": 0.55}
}
```

#### 🔹 Step 2: After Schema Building
```json
{
  "domain": "ml_engineer",
  "hero": {
    "name": "Alice Chen",
    "template": "Building intelligent systems with {tech}",
    "needs_generation": true
  },
  "bio": {
    "structure": ["hook", "background", "expertise", "passion"],
    "tone": "professional_friendly",
    "needs_generation": true
  },
  "projects": [{
    "id": "project_0",
    "title": "Chatbot",
    "raw_description": "Made a bot",
    "featured": true,
    "needs_enhancement": true,
    "target_length": "100-150 words"
  }],
  "skills": {
    "languages": ["Python"],
    "frameworks": ["React", "TensorFlow"],
    "ml_ai": ["Machine Learning"]
  },
  "theme": {
    "primary_color": "#4A90E2",
    "style": "modern_tech"
  }
}
```

#### 🔹 Step 3: After Content Generation (Gemini)
```json
{
  "hero": {
    "name": "Alice Chen",
    "tagline": "Building AI systems that transform user experiences"
  },
  "bio": "I'm a machine learning engineer passionate about creating intelligent systems that solve real-world problems. With expertise in Python, TensorFlow, and modern web technologies, I bridge the gap between cutting-edge AI research and practical applications. Currently, I'm focused on developing conversational AI that enhances user interactions...",
  "projects": [{
    "id": "project_0",
    "title": "Chatbot",
    "description": "Developed an intelligent conversational AI chatbot leveraging natural language processing and machine learning. The system uses TensorFlow to understand user intent and provide contextually relevant responses, significantly improving user engagement and satisfaction.",
    "tech_stack": ["Python", "TensorFlow", "NLP"],
    "featured": true
  }],
  "skills": {...},
  "theme": {...}
}
```

#### 🔹 Step 4: After Validation
```json
{
  "hero": {...},
  "bio": "...",
  "projects": [...],
  "validation": {
    "hero": {"score": 0.9, "passed": true},
    "bio": {"score": 0.85, "passed": true},
    "projects": {"score": 0.88, "passed": true},
    "overall": {"score": 0.87, "passed": true}
  },
  "metadata": {
    "generated_at": "2025-01-04T10:30:00Z",
    "version": "1.0"
  }
}
```

---

## 🎨 How Agents Make Decisions

### Domain Detection Algorithm
```python
def detect_domain(skills, projects):
    # Count keyword occurrences
    ml_score = count_keywords(['machine learning', 'tensorflow', 'nlp'])
    frontend_score = count_keywords(['react', 'vue', 'css'])
    backend_score = count_keywords(['api', 'database', 'server'])
    
    # Decision tree
    if frontend_score >= 2 and backend_score >= 2:
        return 'fullstack_developer'
    
    if ml_score > 3:
        return 'ml_engineer'
    
    return max(scores, key=scores.get)
```

### Content Generation Strategy
```python
# For each section, Gemini receives:
prompt = f"""
Context: {user_data}
Requirements: {length}, {tone}, {style}
Structure: {template}

Generate content that:
1. Matches the tone
2. Stays within length
3. Uses active voice
4. No buzzwords

Output: [section content only]
"""
```

### Quality Scoring Formula
```python
quality_score = (
    name_present * 0.10 +
    email_valid * 0.10 +
    min(skills_count * 0.02, 0.20) +
    min(projects_count * 0.10, 0.30) +
    min(experience_count * 0.05, 0.15) +
    min(education_count * 0.05, 0.10) +
    min(links_count * 0.02, 0.05)
)
```

---

## 🚀 Usage Examples

### Basic Usage
```python
from agents.integration import generate_portfolio

# Your parsed resume data
data = {
    'name': 'Jane Smith',
    'skills': ['Python', 'Django', 'PostgreSQL'],
    'projects': [...]
}

# Generate portfolio
portfolio = await generate_portfolio(data)

# Access results
print(portfolio['hero']['tagline'])
print(portfolio['bio'])
```

### With Custom Configuration
```python
config = {
    'gemini_api_key': 'your-api-key',
    'strict_validation': True,
    'generation': {
        'temperature': 0.8,  # More creative
    }
}

portfolio = await generate_portfolio(data, config)
```

### Regenerate Specific Section
```python
# User doesn't like the hero tagline
preferences = {
    'tone': 'bold',
    'style': 'action-oriented'
}

updated = await regenerate_section(
    portfolio,
    section='hero',
    preferences=preferences
)
```

### Validate Before Processing
```python
from agents.integration import validate_input

is_valid, error = validate_input(data)
if not is_valid:
    print(f"Error: {error}")
else:
    portfolio = await generate_portfolio(data)
```

---

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
export GEMINI_API_KEY="your-gemini-api-key"

# Optional
export LOG_LEVEL="INFO"
```

### Config Dictionary
```python
config = {
    # Gemini settings
    'gemini_api_key': 'key',
    'generation': {
        'temperature': 0.7,      # 0.0-1.0, higher = more creative
        'max_tokens': 2048,
    },
    
    # Validation settings
    'strict_validation': False,  # If True, fails on low quality
    
    # Preprocessing settings
    'preprocessing': {
        'min_quality_score': 0.4
    }
}
```

---

## 🐛 Error Handling

### Common Errors

1. **Missing API Key**
   ```python
   ValueError: GEMINI_API_KEY not found
   ```
   **Fix**: Set environment variable or pass in config

2. **Invalid Input**
   ```python
   ValueError: Either 'name' or 'email' is required
   ```
   **Fix**: Ensure data has required fields

3. **Low Quality Score**
   ```python
   ValueError: Portfolio quality too low: 0.45
   ```
   **Fix**: Provide more complete resume data

4. **Generation Timeout**
   ```python
   TimeoutError: Gemini API request timed out
   ```
   **Fix**: Retry with exponential backoff (built-in)

---

## 📊 Quality Metrics

### What Gets Measured

1. **Data Quality Score** (0.0-1.0)
   - Completeness of input data
   - Calculated by preprocessor

2. **Validation Scores** (0.0-1.0)
   - Hero section quality
   - Bio quality
   - Projects quality
   - Overall portfolio quality

3. **Generation Metadata**
   - Timestamp
   - Model version
   - Processing time

### Quality Thresholds
```python
EXCELLENT = 0.9+   # Ready to deploy
GOOD = 0.7-0.9     # Minor improvements
ACCEPTABLE = 0.5-0.7  # Needs enhancement
POOR = < 0.5       # Requires regeneration
```

---

## 🔐 Security & Privacy

### Data Handling
- ✅ No data is stored permanently
- ✅ API keys are never logged
- ✅ All processing is session-based
- ✅ Gemini API calls are encrypted

### What Gets Sent to Gemini
- User's name, skills, projects
- NOT sent: email, links (kept local)

---

## 🧪 Testing

### Test Individual Agents
```python
# Test preprocessor
from agents.middleware.data_preprocessor import DataPreprocessor

preprocessor = DataPreprocessor({})
cleaned = await preprocessor.preprocess(raw_data)
assert cleaned['metadata']['data_quality_score'] > 0.5

# Test schema builder
from agents.core.schema_builder import SchemaBuilder

builder = SchemaBuilder({})
schema = await builder.build_schema(cleaned)
assert schema['domain'] in ['ml_engineer', 'fullstack_developer', ...]
```

### Integration Tests
```python
# Run full pipeline
from agents.integration import generate_portfolio

portfolio = await generate_portfolio(test_data)
assert portfolio['validation']['overall']['passed'] == True
```

---

## 📈 Performance

### Expected Times (Approximate)
- Preprocessing: ~100ms
- Schema Building: ~200ms
- Content Generation: ~3-5 seconds (Gemini API)
- Validation: ~100ms
- **Total**: ~4-6 seconds

### Optimization Tips
- Use async/await properly
- Batch multiple requests if possible
- Cache schema templates
- Reuse orchestrator instance

---

## 🎓 Key Concepts Summary

| Agent | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Preprocessor** | Raw parsed data | Clean data | Data janitor |
| **Schema Builder** | Clean data | Structure + templates | Architect |
| **Content Generator** | Schema + data | AI-written content | Creative writer |
| **Validator** | Generated content | Quality-checked portfolio | Editor |
| **Orchestrator** | Raw data | Final portfolio | Conductor |

---

## 🎯 Design Principles

1. **Separation of Concerns**: Each agent has ONE job
2. **Pipeline Architecture**: Data flows linearly through stages
3. **Fail Fast**: Validate early, catch errors before Gemini
4. **Quality First**: Multiple validation layers
5. **Async-First**: All I/O is asynchronous
6. **Configurable**: Easy to customize behavior

---

## 🤝 Integration with Other Components

### How Backend Uses This
```python
# In your Flask/FastAPI endpoint
@app.post("/generate-portfolio")
async def generate_endpoint(resume_data: dict):
    # 1. OCR + NLP parsing (your code)
    parsed = parse_resume(resume_data)
    
    # 2. Call agents
    portfolio = await generate_portfolio(parsed)
    
    # 3. Return to frontend
    return {"portfolio": portfolio}
```

### How Frontend Receives Data
```javascript
// Frontend gets this structure
{
  hero: { name, tagline, email, links },
  bio: "...",
  projects: [...],
  skills: { categorized },
  theme: { colors, fonts },
  layout: { hints }
}

// Render portfolio from this data
```

---

## 🔮 Future Enhancements

Possible improvements:
- [ ] Multiple language support
- [ ] Industry-specific templates
- [ ] A/B testing different generations
- [ ] User feedback learning
- [ ] Image generation for projects
- [ ] Video summary generation
- [ ] SEO optimization suggestions

---

## 📚 Additional Resources

- Google Gemini API: https://ai.google.dev/
- Async Python: https://docs.python.org/3/library/asyncio.html
- Agent Design Patterns: See orchestrator.py

---

## 🆘 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: 
```bash
export GEMINI_API_KEY="your-key"
# or
config = {'gemini_api_key': 'your-key'}
```

### Issue: "Quality score too low"
**Solution**: Provide more complete resume data with:
- More skills (aim for 5+)
- Detailed project descriptions
- Experience entries

### Issue: "Generation takes too long"
**Solution**: 
- Check internet connection
- Verify Gemini API status
- Try reducing max_tokens in config

---

## 📝 Notes

**IMPORTANT**: This entire agents system is AI-generated code. It's been designed to be:
- Easy to understand
- Well-documented
- Production-ready
- Maintainable

All code includes extensive comments explaining what each part does and why.

---

**END OF DOCUMENTATION**