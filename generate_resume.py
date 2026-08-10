"""
Resume PDF generator for Piolo Rafael Avenido.
Generates a clean, professional 2-page resume with proper spacing and text wrapping.
"""
import pymupdf

OUT = "/home/cmark/piolo-portfolio/resume.pdf"

# Font files (Liberation Sans = Helvetica metric-compatible)
FONT_REG_FILE = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD_FILE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG_NAME = "lreg"
FONT_BOLD_NAME = "lbold"

# Preload font objects for text measurement
_FONT_REG_OBJ = pymupdf.Font(fontfile=FONT_REG_FILE)
_FONT_BOLD_OBJ = pymupdf.Font(fontfile=FONT_BOLD_FILE)

# --- Page geometry ---
PAGE_W = 595
PAGE_H = 842
MARGIN_L = 50
MARGIN_R = 50
MARGIN_T = 38
MARGIN_B = 40
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# --- Font sizes ---
SIZE_NAME = 17
SIZE_CONTACT = 8
SIZE_SECTION = 10
SIZE_BODY = 8.5
SIZE_SUB = 7.5

# --- Line heights (proper spacing — no overlap) ---
LH_BODY = 12.5
LH_SECTION = 16
LH_SUB = 10.5
GAP_SECTION = 6
GAP_ENTRY = 4

# Wrap width safety margin (font metrics vs render can differ)
WRAP_SAFETY = 12

# --- Colors ---
COLOR_NAME = (0.15, 0.20, 0.45)
COLOR_SECTION = (0.15, 0.20, 0.45)
COLOR_BODY = (0.10, 0.10, 0.10)
COLOR_SUB = (0.30, 0.30, 0.30)


class ResumeBuilder:
    def __init__(self):
        self.doc = pymupdf.open()
        self.page = None
        self.y = 0
        self._new_page()

    def _new_page(self):
        self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)
        # Register fonts on each page so get_text_length works
        self.page.insert_font(fontname=FONT_REG_NAME, fontfile=FONT_REG_FILE)
        self.page.insert_font(fontname=FONT_BOLD_NAME, fontfile=FONT_BOLD_FILE)
        self.y = MARGIN_T

    def _ensure_space(self, needed):
        if self.y + needed > PAGE_H - MARGIN_B:
            self._new_page()

    def _text_w(self, text, bold, size):
        font_obj = _FONT_BOLD_OBJ if bold else _FONT_REG_OBJ
        return font_obj.text_length(text, fontsize=size)

    def _wrap(self, text, bold, size, max_width):
        max_width -= WRAP_SAFETY
        words = text.split()
        lines = []
        current = []
        for word in words:
            trial = " ".join(current + [word])
            if self._text_w(trial, bold, size) <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines

    def _put(self, x, y, text, bold, size, color):
        """Insert text using pre-registered fonts."""
        fontname = FONT_BOLD_NAME if bold else FONT_REG_NAME
        self.page.insert_text(
            pymupdf.Point(x, y),
            text,
            fontname=fontname,
            fontsize=size,
            color=color
        )

    def section_header(self, title):
        self.y += GAP_SECTION
        self._ensure_space(LH_SECTION + 4)
        self._put(MARGIN_L, self.y + SIZE_SECTION, title, True, SIZE_SECTION, COLOR_SECTION)
        text_w = self._text_w(title, True, SIZE_SECTION)
        self.page.draw_line(
            pymupdf.Point(MARGIN_L, self.y + SIZE_SECTION + 3),
            pymupdf.Point(MARGIN_L + text_w + 60, self.y + SIZE_SECTION + 3),
            color=COLOR_SECTION,
            width=0.6
        )
        self.y += LH_SECTION

    def body_line(self, text, indent=0, gap=0):
        x = MARGIN_L + indent
        lines = self._wrap(text, False, SIZE_BODY, CONTENT_W - indent)
        for line in lines:
            self._ensure_space(LH_BODY)
            self._put(x, self.y + SIZE_BODY, line, False, SIZE_BODY, COLOR_BODY)
            self.y += LH_BODY
        if gap:
            self.y += gap

    def bullet(self, text, indent=22):
        bullet_x = MARGIN_L + 12
        text_x = MARGIN_L + indent
        max_text_w = CONTENT_W - indent
        lines = self._wrap(text, False, SIZE_BODY, max_text_w)
        for i, line in enumerate(lines):
            self._ensure_space(LH_BODY)
            if i == 0:
                self._put(bullet_x, self.y + SIZE_BODY, "\u2022", False, SIZE_BODY, COLOR_BODY)
            self._put(text_x, self.y + SIZE_BODY, line, False, SIZE_BODY, COLOR_BODY)
            self.y += LH_BODY

    def entry_header(self, title, subtitle=None):
        self._ensure_space(LH_SUB + LH_BODY + 2)
        self._put(MARGIN_L, self.y + SIZE_BODY, title, True, SIZE_BODY, COLOR_BODY)
        self.y += LH_BODY
        if subtitle:
            self._put(MARGIN_L, self.y + SIZE_SUB, subtitle, False, SIZE_SUB, COLOR_SUB)
            self.y += LH_SUB

    def sub_label(self, text):
        self._ensure_space(LH_BODY + 2)
        self._put(MARGIN_L, self.y + SIZE_BODY, text, True, SIZE_BODY, COLOR_BODY)
        self.y += LH_BODY

    def build(self):
        self._header()
        self._summary()
        self._education()
        self._experience()
        self._projects()
        self._skills()
        self._certifications()
        self._awards()
        self._references()
        self._footer()
        self.doc.save(OUT)
        self.doc.close()
        print(f"Resume saved to {OUT}")

    def _header(self):
        self._put(MARGIN_L, self.y + SIZE_NAME, "PIOLO RAFAEL AVENIDO", True, SIZE_NAME, COLOR_NAME)
        self.y += SIZE_NAME + 8
        contact = "piolo.avenido123@gmail.com  |  09186813030  |  LinkedIn  |  GitHub  |  Portfolio"
        self._put(MARGIN_L, self.y + SIZE_CONTACT, contact, False, SIZE_CONTACT, COLOR_BODY)
        self.y += SIZE_CONTACT + 5
        self._put(MARGIN_L, self.y + SIZE_CONTACT, "Barangay San Francisco, Magarao, Camarines Sur, 4403, Philippines", False, SIZE_CONTACT, COLOR_BODY)
        self.y += SIZE_CONTACT + 8

    def _summary(self):
        self.section_header("SUMMARY")
        self.body_line(
            "A detail-oriented Information Technology graduate and AI developer with hands-on "
            "experience building and deploying AI applications using Python, FastAPI, and LLM "
            "integration. Developed and deployed 5 solo AI projects including a resume analyzer, "
            "a RAG-based document Q&A system, a lead enrichment pipeline, and a sentiment analysis "
            "dashboard. Hosted on a self-managed Linux server with Docker, Caddy, and Cloudflare. "
            "Proficient in leveraging automation tools including n8n and GHL to develop and optimize "
            "marketing-centric workflows that enhance efficiency and campaign execution. Experienced "
            "in communicating with clients, coordinating with cross-functional teams, and managing "
            "multiple projects from concept to deployment. Certified in Claude and the Anthropic "
            "platform. Seeking to contribute to a professional team as an AI developer or automation "
            "engineer."
        )
        self.y += 4

    def _education(self):
        self.section_header("EDUCATION")
        self.entry_header(
            "Baccalaureate Degree: Bachelor of Science in Information Technology",
            "University of Nueva C\u00e1ceres, Naga City, 2019 \u00b7 2026"
        )
        self.y += 4

    def _experience(self):
        self.section_header("WORK EXPERIENCE")

        self.entry_header(
            "Administrative Assistant (Student Assistant)",
            "University of Nueva Caceres \u00b7 Office of the Vice President for Administration, 2019\u20132021"
        )
        self.bullet("Provided daily administrative support, including file management, calendar coordination, "
                     "internal communications, on-site venue preparations, and office logistics.")
        self.bullet("Maintained organized records, assisted in scheduling meetings, and prepared office materials.")
        self.bullet("Gained experience handling confidential documents and managing task priorities effectively.")
        self.y += GAP_ENTRY

        self.entry_header("Technical Support Associate", "Relaytask, 2025")
        self.bullet("Developed several workflow automations using n8n and GHL automations for executive use and "
                     "company operations, and assisted in the development of several systems the company offers, "
                     "such as services catered to a niche market.")
        self.bullet("Handled communications with outside sources and clients regarding user needs and services "
                     "offered, leading meetings that spearheaded several projects in the market.")
        self.bullet("Responsible for troubleshooting and maintenance of hardware and software used on-site.")
        self.bullet("Assisted in backend development in several programs and systems that the company offers.")
        self.y += GAP_ENTRY

        self.entry_header("Website Designer/Developer", "Relaytask, 2025")
        self.bullet("Designed, assisted, and implemented several working websites under Relaytask in gaining "
                     "visibility and making funnel websites to garner leads from social media and other sources.")
        self.bullet("Developed websites using WordPress and GHL, accompanied by the responsibility to track "
                     "and monitor page views and uptime.")
        self.bullet("Handled implementing affiliate marketing with GHL on several websites.")
        self.y += 4

    def _projects(self):
        self.section_header("PROJECTS")
        self.sub_label("Solo AI Projects (all live and open-source):")

        self.bullet("AI Resume Analyzer \u00b7 Python/FastAPI app that analyzes resumes against job descriptions "
                     "using LLM-powered analysis. Live at resume.betamaxgroup.tech. "
                     "GitHub: github.com/pioloavenido123-source/ai-resume-analyzer")
        self.bullet("AI Document Q&A (RAG) \u00b7 Upload any PDF and ask questions with source citations. Uses "
                     "sentence embeddings + vector search + deepseek-v4-flash. Live at docqa.betamaxgroup.tech. "
                     "GitHub: github.com/pioloavenido123-source/ai-document-qa-rag")
        self.bullet("Lead Enrichment Pipeline \u00b7 Enter a company website, AI extracts business intelligence "
                     "(contact info, social links). Python/FastAPI + web scraping + LLM. Live at "
                     "leads.betamaxgroup.tech. GitHub: github.com/pioloavenido123-source/ai-lead-enrichment-pipeline")
        self.bullet("Sentiment Analysis Dashboard \u00b7 Paste reviews or feedback, AI classifies sentiment with "
                     "charts. Python/FastAPI + Chart.js + LLM. Live at sentiment.betamaxgroup.tech. "
                     "GitHub: github.com/pioloavenido123-source/sentiment-analysis-dashboard")
        self.bullet("PioloBot Chatbot \u00b7 AI chatbot embedded on portfolio website with conversation memory, "
                     "session persistence, and natural language responses. Python + LLM. Live at "
                     "piolo.betamaxgroup.tech. GitHub: github.com/pioloavenido123-source/piolo-portfolio")

        self.y += 4
        self.sub_label("Collaborative Projects:")
        self.bullet("Zimmy POS \u00b7 Point-of-sale system for food businesses (React, Node.js, PostgreSQL)")
        self.bullet("n8n Workflow Automations \u00b7 Marketing-centric workflow automations using n8n and GHL at Relaytask")
        self.bullet("Relay Task \u00b7 Task management and HOA management platform")
        self.bullet("Deskline.co \u00b7 Web platform built with WordPress and GHL")
        self.y += 4

    def _skills(self):
        self.section_header("SKILLS AND ABILITIES")
        self.sub_label("Technical Skills")
        self.bullet("Programming Languages: Python, JavaScript, C++, Java, PHP")
        self.bullet("AI/ML: LLM Integration (Ollama, OpenAI-compatible APIs, Claude/Anthropic), Prompt Engineering, "
                     "RAG (Retrieval-Augmented Generation), Embeddings & Vector Search, Sentiment Analysis")
        self.bullet("Backend Development: FastAPI, Node.js, REST API design")
        self.bullet("Frontend Development: HTML/CSS, React, Progressive Web Apps")
        self.bullet("Deployment & Infrastructure: Docker, Caddy reverse proxy, Cloudflare, Linux server administration")
        self.bullet("Automation: n8n workflow automation, Go High Level (GHL) automation, lead enrichment pipelines")
        self.bullet("Web Development: WordPress, GHL web funnels, SEO-focused landing pages")
        self.bullet("Data Analytics: Data cleaning, sorting, analysis, and visualization")
        self.bullet("Database: SQL")
        self.bullet("Tools: Google Workspace, Canva, Git/GitHub, Claude Code (CLI)")
        self.y += 4

        self.sub_label("Personal Skills")
        self.bullet("Communication skills (written and verbal) \u00b7 Awarded English Immersive Environment; "
                     "written communications to organizations and university officials")
        self.bullet("Leadership skills \u00b7 Spearheaded and assisted projects at the university and "
                     "extracurricular activities; served as Manager on group thesis \"Web-Based POS System "
                     "for Local Cafe Shop in Naga City\"")
        self.bullet("Project management \u00b7 Led a team developing a Progressive Web App for cafe business "
                     "owners with features for sales tracking, inventory management, and customer service")
        self.bullet("Good work ethic \u00b7 Respectful, accountable, strong time management balancing personal, "
                     "academic, and professional responsibilities")
        self.y += 4

    def _certifications(self):
        self.section_header("TRAINING / CERTIFICATION / LICENSE")
        self.bullet("Claude 101 \u00b7 Anthropic, August 2026")
        self.bullet("Claude Code 101 \u00b7 Anthropic, August 2026")
        self.bullet("Claude Platform 101 \u00b7 Anthropic, August 2026")
        self.bullet("Introduction to Cybersecurity \u00b7 Cisco, 19 Dec 2024")
        self.bullet("Learning SQL Programming \u00b7 LinkedIn Learning, 2023")
        self.bullet("React Essential Training \u00b7 LinkedIn Learning, 2025")
        self.bullet("React: Building Progressive Web Apps (PWAs) \u00b7 LinkedIn Learning, 2025")
        self.bullet("Node.js Essential Training \u00b7 LinkedIn Learning, 2025")
        self.bullet("Administrative Professional Foundations \u00b7 LinkedIn Learning, 2025")
        self.bullet("Git Essential Training (2023) \u00b7 LinkedIn Learning, 2025")
        self.y += 4

    def _awards(self):
        self.section_header("AWARDS")
        self.bullet("English for Immersive Environment (EIE) Department Representative \u00b7 University of Nueva C\u00e1ceres")
        self.bullet("English for Immersive Environment (EIE) Student Assistant \u00b7 University of Nueva C\u00e1ceres, 2024")
        self.bullet("Certificate of Recognition \u00b7 Relaytask, 2025")
        self.y += 4

    def _references(self):
        self.section_header("REFERENCES")
        self.bullet("Faith Villamor \u00b7 Registrar Clerk, University of Nueva Caceres \u00b7 09511644059 / villamorfaith@gmail.com")
        self.bullet("Mark Alfonso A. Cervantes \u00b7 Software Developer, Somisomi Franchise Ltd. \u00b7 0936 598 9544 / mark.cervantes@somisomi.com")
        self.bullet("Samantha Espinas \u00b7 Network Engineer, Accenture \u00b7 09933075331")
        self.y += 8

    def _footer(self):
        self._ensure_space(40)
        self._put(MARGIN_L, self.y + SIZE_BODY, "I certify that the above information is true and correct.", False, SIZE_BODY, COLOR_BODY)
        self.y += 24
        self._put(MARGIN_L, self.y + SIZE_SECTION, "Piolo Rafael Avenido", True, SIZE_SECTION, COLOR_NAME)


if __name__ == "__main__":
    builder = ResumeBuilder()
    builder.build()