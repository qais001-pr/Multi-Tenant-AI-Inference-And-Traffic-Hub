import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import { ArrowUp, User, Bot, Cpu, Mail, ArrowRight } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function App() {
  const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

  // 1. Core Authentication States
  const [email, setEmail] = useState(
    () => localStorage.getItem("chat_user_email") || "",
  );
  const [emailInput, setEmailInput] = useState("");

  const [message, setmessage] = useState("");
  const [loading, setloading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const textareaRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // 2. Handle Authentication Guard Form
  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    if (!emailInput.trim()) return;
    try {
      const response = await fetch(`${apiUrl}/emails/add-user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: emailInput }),
      });
      if (response.ok) {
        const result = await response.json();
        console.log(result?.data?.id);
        localStorage.setItem("chat_user_email", emailInput);
        localStorage.setItem("chat_user_id", result?.data?.id);
        setEmail(emailInput);
      } else {
        alert("Something Went Wrong!");
        return;
      }
    } catch (error) {}
  };

  const submitMessage = async () => {
    if (!message.trim() || loading) return;

    const userPrompt = message;
    setmessage("");

    setChatHistory((prev) => [...prev, { role: "user", content: userPrompt }]);
    setloading(true);

    try {
      // Optional: You can append the email as a query parameter if your backend requires it for logging/auth
      const response = await fetch(
        `${apiUrl}/chat?mess=${encodeURIComponent(userPrompt)}&user_id=${parseInt(localStorage.getItem("chat_user_id"))}`,
      );

      if (response.ok) {
        const result = await response.json();
        const assistantReply =
          result?.detail?.message?.content || "No response received.";

        const meta = {
          model: result?.detail?.model || "Unknown",
          evalCount: result?.detail?.eval_count || 0,
          totalDuration: result?.detail?.total_duration
            ? `${(result.detail.total_duration / 1e9).toFixed(2)}s`
            : "N/A",
        };

        setChatHistory((prev) => [
          ...prev,
          { role: "assistant", content: assistantReply, metadata: meta },
        ]);
      } else {
        setChatHistory((prev) => [
          ...prev,
          { role: "error", content: "Failed to fetch response." },
        ]);
      }
    } catch (error) {
      console.error(error);
      setChatHistory((prev) => [
        ...prev,
        { role: "error", content: "An error occurred." },
      ]);
    } finally {
      setloading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  // Optional Logout Function to clear user access
  const handleLogout = () => {
    localStorage.removeItem("chat_user_email");
    localStorage.removeItem("chat_user_id");
    setEmail("");
    setChatHistory([]);
  };

  if (!email) {
    return (
      <div className="auth-gate-container">
        <div className="auth-card">
          <div className="auth-icon-wrapper">
            <Bot size={32} className="bot-icon" />
          </div>
          <h2>Welcome to LLAMA Chat</h2>
          <p>Please enter your email to access the conversation dashboard.</p>

          <form onSubmit={handleAuthSubmit} className="auth-form">
            <div className="auth-input-container">
              <Mail size={18} className="auth-mail-icon" />
              <input
                type="email"
                required
                placeholder="name@company.com"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                className="auth-input"
              />
            </div>
            <button type="submit" className="auth-submit-btn">
              Continue <ArrowRight size={16} />
            </button>
          </form>
        </div>
      </div>
    );
  }

  // If email exists, render the standard active chat panel layout
  return (
    <div className="chat-layout">
      {/* Tiny active session banner on top right */}
      <div className="session-header">
        <span className="session-email">
          {email} {`${localStorage.getItem("chat_user_id")}`}
        </span>
        <button onClick={handleLogout} className="logout-btn">
          Disconnect
        </button>
      </div>

      {chatHistory.length === 0 ? (
        <div className="welcome-container">
          <h1 className="chat-title">What's on your mind today?</h1>
        </div>
      ) : (
        <div className="chat-history">
          {chatHistory.map((chat, index) => (
            <div key={index} className={`chat-bubble-wrapper ${chat.role}`}>
              <div className="avatar">
                {chat.role === "user" ? (
                  <User size={16} className="user-icon" />
                ) : (
                  <Bot size={16} className="bot-icon" />
                )}
              </div>
              <div className="chat-content-block">
                <div className="chat-bubble">
                  <ReactMarkdown
                    children={chat.content}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline && match ? (
                          <div className="code-block-container">
                            <div className="code-block-header">{match[1]}</div>
                            <SyntaxHighlighter
                              {...props}
                              children={String(children).replace(/\n$/, "")}
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                            />
                          </div>
                        ) : (
                          <code {...props} className={className}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  />
                </div>

                {chat.role === "assistant" && chat.metadata && (
                  <div className="meta-badge-container">
                    <Cpu size={12} className="meta-icon" />
                    <span>{chat.metadata.model}</span>
                    {/*  <span className="meta-divider">•</span>
                    <span>{chat.metadata.evalCount} tokens</span> */}
                    <span className="meta-divider">•</span>
                    <span>{chat.metadata.totalDuration}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-bubble-wrapper assistant loading-state">
              <div className="avatar">
                <Bot size={16} className="bot-icon" />
              </div>
              <div className="chat-bubble dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      )}

      <div className="input-wrapper">
        <div className="input-field-container">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setmessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message To LLAMA..."
            className="chat-input"
            rows="1"
          />
          <button
            className="send-btn"
            aria-label="Send message"
            onClick={submitMessage}
            disabled={!message.trim() || loading}
          >
            <ArrowUp size={18} />
          </button>
        </div>
        <p className="disclaimer-text">
          LLAMA can make mistakes. Consider checking important information.
        </p>
      </div>
    </div>
  );
}
