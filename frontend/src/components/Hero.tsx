import { Paperclip, Palette, MessageSquare, ArrowUp, AudioLines, X, Loader2 } from "lucide-react";
import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";

export const Hero = () => {
  const [prompt, setPrompt] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!prompt.trim() && !file) return;

    try {
      let jobId = null;

      // 1. If file attached, upload it first
      if (file) {
        setIsUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        // Using direct URL as per user context (adjust if proxy exists)
        const response = await axios.post("http://localhost:8000/api/v1/resume/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          }
        });

        jobId = response.data.job_id;
        toast.success("Resume uploaded successfully!");
      }

      // 2. Navigate to editor with context
      const params = new URLSearchParams();
      if (prompt.trim()) params.set("prompt", prompt);
      if (jobId) params.set("jobId", jobId);
      if (file) params.set("fileName", file.name); // Keep for UI reference

      navigate(`/editor?${params.toString()}`);

    } catch (error) {
      console.error("Upload failed", error);
      toast.error("Failed to upload resume. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      // Basic validation
      if (selectedFile.type === "application/pdf" || selectedFile.type.startsWith("image/")) {
        setFile(selectedFile);
        toast.success(`Attached ${selectedFile.name}`);
      } else {
        toast.error("Please upload a PDF or Image file");
      }
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-16 gradient-obsidian overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-glow-purple/20 rounded-full blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-glow-pink/20 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-glow-blue/20 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: "2s" }} />
      </div>

      <div className="relative z-10 container mx-auto px-4 text-center">
        {/* Main Heading */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6">
          Build something <span className="text-gradient">Showcase</span>
        </h1>

        {/* Subheading */}
        <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
          Create apps and websites by chatting with AI
        </p>

        {/* Chat Input Box */}
        <div className="max-w-2xl mx-auto">
          <div className={`border-gradient rounded-2xl p-1 transition-all duration-300 ${isFocused ? 'glow-purple' : ''}`}>
            <div className="bg-obsidian-light rounded-xl p-4">
              {/* Input area */}
              <div className="min-h-[80px] mb-4">
                {file && (
                  <div className="flex items-center gap-2 mb-2 bg-obsidian-lighter w-fit px-3 py-1 rounded-full border border-border/50">
                    <Paperclip className="h-3 w-3 text-primary" />
                    <span className="text-xs text-foreground/80">{file.name}</span>
                    <button onClick={removeFile} className="hover:text-destructive transition-colors">
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                )}
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask Showcase to create a landing page for my..."
                  className="w-full bg-transparent text-foreground placeholder:text-muted-foreground resize-none focus:outline-none text-left min-h-[60px]"
                  rows={2}
                />
              </div>

              {/* Action bar */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <span className="text-lg">+</span>
                  </button>

                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept=".pdf,image/*"
                    onChange={handleFileChange}
                  />

                  <button
                    onClick={handleAttachClick}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors ${file ? 'text-primary bg-primary/10' : 'text-muted-foreground hover:text-foreground'}`}
                  >
                    <Paperclip className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Attach</span>
                  </button>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <Palette className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Theme</span>
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <MessageSquare className="h-4 w-4" />
                    <span className="text-sm hidden sm:inline">Chat</span>
                  </button>
                  <button className="p-2 rounded-lg hover:bg-obsidian-lighter transition-colors text-muted-foreground hover:text-foreground">
                    <AudioLines className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={(!prompt.trim() && !file) || isUploading}
                    className="p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowUp className="h-4 w-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
