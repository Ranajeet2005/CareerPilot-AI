
import { useState } from "react";

const API =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  // Navigation
  const [page, setPage] = useState("Dashboard");

  // Loading and API states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  // Resume Analyzer
  const [resume, setResume] = useState("");

  // Job Matching
  const [skills, setSkills] = useState(
    "Python, FastAPI, Machine Learning, PostgreSQL"
  );
  const [preferredRoles, setPreferredRoles] = useState(
    "AI Engineer, Python Developer"
  );
  const [location, setLocation] = useState("India");

  // AI Career Chat
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  // Job Search
  const [searchQuery, setSearchQuery] = useState("");

  const menu = [
    "Dashboard",
    "Resume Analyzer",
    "Job Matching",
    "AI Career Chat",
    "Job Search"
  ];

  // Convert API errors into readable messages
  function getErrorMessage(data) {
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => {
          const field = item.loc?.slice(1).join(".") || "Request";
          return `${field}: ${item.msg}`;
        })
        .join("\n");
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (typeof data.message === "string") {
      return data.message;
    }

    return "Something went wrong. Please try again.";
  }

  // Generic API request function
  async function request(path, method = "GET", body = null) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API}${path}`, {
        method,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        ...(body !== null
          ? { body: JSON.stringify(body) }
          : {})
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(getErrorMessage(data));
      }

      let output =
        data.analysis ??
        data.answer ??
        data.ai_explanation ??
        data.matches ??
        data.recommendations ??
        data.results ??
        data.parsed_resume ??
        data;

      if (typeof output !== "string") {
        output = JSON.stringify(output, null, 2);
      }

      setResult(output);
      return data;

    } catch (err) {
      setError(err.message || "Unable to connect to the server.");
      return null;

    } finally {
      setLoading(false);
    }
  }

  // Reset page results
  function navigateTo(item) {
    setPage(item);
    setResult(null);
    setError("");
  }

  // Resume Analyzer
  async function analyzeResume() {
    if (resume.trim().length < 30) {
      setError("Please enter at least 30 characters of resume text.");
      return;
    }

    await request("/ai/analyze-resume", "POST", {
      resume_text: resume.trim()
    });
  }

  // Job Matching
  async function findJobMatches() {
    const skillList = skills
      .split(",")
      .map((skill) => skill.trim())
      .filter(Boolean);

    const roleList = preferredRoles
      .split(",")
      .map((role) => role.trim())
      .filter(Boolean);

    if (skillList.length === 0) {
      setError("Please enter at least one skill.");
      return;
    }

    await request("/jobs/match", "POST", {
      skills: skillList,
      preferred_roles: roleList,
      location: location.trim() || null
    });
  }

  // AI Career Chat
  async function sendMessage() {
    if (!message.trim()) return;

    const userMessage = message.trim();

    const response = await request("/ai/chat", "POST", {
      message: userMessage,
      skills: skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    });

    if (response) {
      setChatHistory((previous) => [
        ...previous,
        {
          role: "user",
          content: userMessage
        },
        {
          role: "assistant",
          content: response.answer || "No response received."
        }
      ]);

      setMessage("");
      setResult(null);
    }
  }

  // Job Search
  async function searchJobs() {
    if (!searchQuery.trim()) {
      setError("Please enter a job title or skill to search.");
      return;
    }

    await request(
      `/jobs/search?query=${encodeURIComponent(searchQuery.trim())}`
    );
  }

  // Render API result
  function ResultSection() {
    if (!result && !error) return null;

    return (
      <div className="result-section">
        {error && (
          <div className="error-message">
            <h3>Request Failed</h3>
            <pre>{error}</pre>
          </div>
        )}

        {result && (
          <>
            <h2>Results</h2>
            <pre className="analysis-result">{result}</pre>
          </>
        )}
      </div>
    );
  }

  // Main page content
  function renderContent() {
    // Dashboard
    if (page === "Dashboard") {
      return (
        <>
          <h1>Welcome to CareerPilot AI</h1>
          <p className="muted">
            Your personal AI-powered career assistant.
          </p>

          <div className="cards">
            {menu.slice(1).map((item) => (
              <button
                className="feature-card"
                key={item}
                onClick={() => navigateTo(item)}
              >
                <h3>{item}</h3>
                <p>Explore {item.toLowerCase()} tools.</p>
                <span>Open →</span>
              </button>
            ))}
          </div>

          <div className="panel">
            <h2>CareerPilot AI</h2>
            <p className="muted">
              AI-powered career guidance, resume analysis,
              skill-based job matching and career assistance.
            </p>
            <p>
              AI Provider: <strong>Groq</strong>
            </p>
            <p>
              Backend API: <strong>{API}</strong>
            </p>
          </div>
        </>
      );
    }

    // Resume Analyzer
    if (page === "Resume Analyzer") {
      return (
        <div className="panel">
          <h1>Resume Analyzer</h1>
          <p className="muted">
            Get AI-powered feedback on your resume.
          </p>

          <textarea
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            placeholder="Paste your resume text here..."
            rows={12}
          />

          <button
            onClick={analyzeResume}
            disabled={!resume.trim() || loading}
          >
            {loading ? "Analyzing Resume..." : "Analyze Resume"}
          </button>

          <ResultSection />
        </div>
      );
    }

    // Job Matching
    if (page === "Job Matching") {
      return (
        <div className="panel">
          <h1>Job Matching</h1>
          <p className="muted">
            Find jobs based on your skills and preferred roles.
          </p>

          <label>Your Skills</label>
          <textarea
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="Python, Java, FastAPI, Machine Learning"
            rows={4}
          />

          <label>Preferred Roles</label>
          <input
            type="text"
            value={preferredRoles}
            onChange={(e) => setPreferredRoles(e.target.value)}
            placeholder="AI Engineer, Python Developer"
          />

          <label>Preferred Location</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="India"
          />

          <button
            onClick={findJobMatches}
            disabled={loading}
          >
            {loading ? "Finding Matches..." : "Find Job Matches"}
          </button>

          <ResultSection />
        </div>
      );
    }

    // AI Career Chat
    if (page === "AI Career Chat") {
      return (
        <div className="panel">
          <h1>AI Career Assistant</h1>
          <p className="muted">
            Ask CareerPilot AI about careers, internships,
            programming and interview preparation.
          </p>

          <div className="chat-container">
            {chatHistory.length === 0 && (
              <div className="chat-welcome">
                <h3>Hello! I'm CareerPilot AI.</h3>
                <p>
                  How can I help you with your career today?
                </p>
              </div>
            )}

            {chatHistory.map((chat, index) => (
              <div
                key={index}
                className={`chat-message ${chat.role}`}
              >
                <strong>
                  {chat.role === "user" ? "You" : "CareerPilot AI"}
                </strong>
                <p>{chat.content}</p>
              </div>
            ))}
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about AI internships, Python, DSA, interviews..."
            rows={3}
          />

          <button
            onClick={sendMessage}
            disabled={!message.trim() || loading}
          >
            {loading ? "Thinking..." : "Send Message"}
          </button>

          <button
            className="secondary-button"
            onClick={() => {
              setChatHistory([]);
              setError("");
            }}
            disabled={loading || chatHistory.length === 0}
          >
            Clear Chat
          </button>
        </div>
      );
    }

    // Job Search
    if (page === "Job Search") {
      return (
        <div className="panel">
          <h1>Job Search</h1>
          <p className="muted">
            Search the available sample job database.
          </p>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Python Developer, AI Engineer..."
            onKeyDown={(e) => {
              if (e.key === "Enter") searchJobs();
            }}
          />

          <button
            onClick={searchJobs}
            disabled={!searchQuery.trim() || loading}
          >
            {loading ? "Searching..." : "Search Jobs"}
          </button>

          <ResultSection />
        </div>
      );
    }

    return <h1>Page not found</h1>;
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="logo">
          <h2>CareerPilot AI</h2>
          <span>Career Intelligence Platform</span>
        </div>

        <nav>
          {menu.map((item) => (
            <button
              key={item}
              className={page === item ? "active" : ""}
              onClick={() => navigateTo(item)}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span>Version 2.0.0</span>
          <span>Powered by Groq</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="muted">CareerPilot AI / </span>
            <strong>{page}</strong>
          </div>

          <div className="provider-status">
            <span className="status-dot"></span>
            Groq AI
          </div>
        </header>

        <section className="content-area">
          {renderContent()}
        </section>
      </main>
    </div>
  );
}

export default App;
