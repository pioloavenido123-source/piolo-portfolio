"""
Resume PDF generator for Piolo Rafael Avenido.
Matches the original resume design: Times New Roman (Liberation Serif),
11pt body, US Letter, black text, simple horizontal rules under section headers.
"""
import pymupdf

OUT = "/home/cmark/piolo-portfolio/Piolo Rafael Avenido CV-Resume.pdf"

# Liberation Serif = Times New Roman metric-compatible
FONT_REG_FILE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_BOLD_FILE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_ITALIC_FILE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_REG_NAME = "serif"
FONT_BOLD_NAME = "serifb"
FONT_ITALIC_NAME = "serifi"

_FONT_REG_OBJ = pymupdf.Font(fontfile=FONT_REG_FILE)
_FONT_BOLD_OBJ = pymupdf.Font(fontfile=FONT_BOLD_FILE)

# --- Page geometry (US Letter, matching original) ---
PAGE_W = 612
PAGE_H = 792
MARGIN_L = 72
MARGIN_R = 72
MARGIN_T = 60
MARGIN_B = 54
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# --- Font sizes (matching original) ---
SIZE_NAME = 15
SIZE_CONTACT = 11
SIZE_SECTION = 11
SIZE_BODY = 11
SIZE_SUB = 11

# --- Line heights ---
LH_BODY = 15
LH_SECTION = 18
GAP_SECTION = 8
GAP_ENTRY = 6
BULLET_INDENT = 18

WRAP_SAFETY = 8

# --- Colors (black, matching original) ---
COLOR_BLACK = (0, 0, 0)


class ResumeBuilder:
    def __init__(self):
        self.doc = pymupdf.open()
        self.page = None
        self.y = 0
        self._new_page()

    def _new_page(self):
        self.page = self.doc.new_page(width=PAGE_W, height=PAGE_H)
        self.page.insert_font(fontname=FONT_REG_NAME, fontfile=FONT_REG_FILE)
        self.page.insert_font(fontname=FONT_BOLD_NAME, fontfile=FONT_BOLD_FILE)
        self.page.insert_font(fontname=FONT_ITALIC_NAME, fontfile=FONT_ITALIC_FILE)
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

    def _put(self, x, y, text, bold, size, color=COLOR_BLACK, italic=False):
        if italic:
            fontname = FONT_ITALIC_NAME
        elif bold:
            fontname = FONT_BOLD_NAME
        else:
            fontname = FONT_REG_NAME
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
        self._put(MARGIN_L, self.y + SIZE_SECTION, title, True, SIZE_SECTION)
        # Horizontal rule under section header
        self.page.draw_line(
            pymupdf.Point(MARGIN_L, self.y + SIZE_SECTION + 2),
            pymupdf.Point(MARGIN_L + CONTENT_W, self.y + SIZE_SECTION + 2),
            color=COLOR_BLACK,
            width=0.5
        )
        self.y += LH_SECTION

    def body_line(self, text, indent=0, gap=0):
        x = MARGIN_L + indent
        lines = self._wrap(text, False, SIZE_BODY, CONTENT_W - indent)
        for line in lines:
            self._ensure_space(LH_BODY)
            self._put(x, self.y + SIZE_BODY, line, False, SIZE_BODY)
            self.y += LH_BODY
        if gap:
            self.y += gap

    def bullet(self, text, indent=BULLET_INDENT):
        bullet_x = MARGIN_L + 4
        text_x = MARGIN_L + indent
        max_text_w = CONTENT_W - indent
        lines = self._wrap(text, False, SIZE_BODY, max_text_w)
        for i, line in enumerate(lines):
            self._ensure_space(LH_BODY)
            if i == 0:
                self._put(bullet_x, self.y + SIZE_BODY, "\u2022", False, SIZE_BODY)
            self._put(text_x, self.y + SIZE_BODY, line, False, SIZE_BODY)
            self.y += LH_BODY

    def sub_bullet(self, text, indent=BULLET_INDENT + 12):
        bullet_x = MARGIN_L + BULLET_INDENT + 4
        text_x = MARGIN_L + indent
        max_text_w = CONTENT_W - indent
        lines = self._wrap(text, False, SIZE_BODY, max_text_w)
        for i, line in enumerate(lines):
            self._ensure_space(LH_BODY)
            if i == 0:
                self._put(bullet_x, self.y + SIZE_BODY, "-", False, SIZE_BODY)
            self._put(text_x, self.y + SIZE_BODY, line, False, SIZE_BODY)
            self.y += LH_BODY

    def entry_header(self, title, subtitle=None, date=None):
        self._ensure_space(LH_BODY + (LH_BODY if subtitle else 0) + 2)
        self._put(MARGIN_L, self.y + SIZE_BODY, title, True, SIZE_BODY)
        if date:
            # Right-align date
            date_w = self._text_w(date, False, SIZE_BODY)
            self._put(MARGIN_L + CONTENT_W - date_w, self.y + SIZE_BODY, date, False, SIZE_BODY)
        self.y += LH_BODY
        if subtitle:
            self._put(MARGIN_L, self.y + SIZE_BODY, subtitle, False, SIZE_BODY)
            self.y += LH_BODY

    def sub_label(self, text):
        self._ensure_space(LH_BODY + 2)
        self._put(MARGIN_L, self.y + SIZE_BODY, text, True, SIZE_BODY)
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
        self._put(MARGIN_L, self.y + SIZE_NAME, "PIOLO RAFAEL AVENIDO", True, SIZE_NAME)
        self.y += SIZE_NAME + 6
        contact = "piolo.avenido123@gmail.com  |  09186813030  |  09919542477"
        self._put(MARGIN_L, self.y + SIZE_CONTACT, contact, False, SIZE_CONTACT)
        self.y += SIZE_CONTACT + 2
        self._put(MARGIN_L, self.y + SIZE_CONTACT, "LinkedIn: linkedin.com/in/piolo-rafael-avenido  |  GitHub: github.com/pioloavenido123-source", False, SIZE_CONTACT)
        self.y += SIZE_CONTACT + 2
        self._put(MARGIN_L, self.y + SIZE_CONTACT, "Portfolio: piolo-portfolio.vercel.app", False, SIZE_CONTACT)
        self.y += SIZE_CONTACT + 2
        self._put(MARGIN_L, self.y + SIZE_CONTACT, "Barangay San Francisco, Magarao, Camarines Sur, 4403, Philippines", False, SIZE_CONTACT)
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
            "multiple projects from concept to deployment. Seeking to contribute to a professional "
            "team as an AI developer or automation engineer."
        )
        self.y += 4

    def _education(self):
        self.section_header("EDUCATION")
        self.entry_header(
            "Baccalaureate Degree: Bachelor of Science in Information Technology",
            "University of Nueva C\u00e1ceres, Naga City",
            "2019 \u2013 2026"
        )
        self.y += 4

    def _experience(self):
        self.section_header("WORK EXPERIENCE")

        self.entry_header(
            "Administrative Assistant (Student Assistant)",
            "University of Nueva Caceres \u2013 Office of the Vice President for Administration",
            "2019\u20132021"
        )
        self.bullet("Provided daily administrative support, including file management, calendar coordination, "
                     "inventory, communications, on-site venue preparations, and internal communications.")
        self.bullet("Maintained organized records, assisted in scheduling meetings, and prepared office materials.")
        self.bullet("Gained experience handling confidential documents and managing task priorities effectively.")
        self.y += GAP_ENTRY

        self.entry_header("Technical Support Associate", "Relaytask", "2025")
        self.bullet("Developed several workflow automations using n8n and GHL automations for executive use and "
                     "company operations, and assisted in the development of several systems the company offers, "
                     "such as services catered to a niche market.")
        self.bullet("Handled communications with outside sources and clients regarding user needs and services "
                     "offered, leading meetings that spearheaded several projects in the market.")
        self.bullet("Responsible for troubleshooting and maintenance of hardware and software used on-site.")
        self.bullet("Assisted in backend development in several programs and systems that the company offers.")
        self.y += GAP_ENTRY

        self.entry_header("Website Designer/Developer", "Relaytask", "2025")
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
        self.bullet("AI/ML: LLM Integration (Ollama, OpenAI-compatible APIs), Prompt Engineering, "
                     "RAG (Retrieval-Augmented Generation), Embeddings & Vector Search, Sentiment Analysis")
        self.bullet("AI Tools: Claude, ChatGPT, Hermes Agent, Ollama")
        self.bullet("Backend Development: FastAPI, Node.js, REST API design")
        self.bullet("Frontend Development: HTML/CSS, React, Progressive Web Apps")
        self.bullet("Deployment & Infrastructure: Docker, Caddy reverse proxy, Cloudflare, Linux server administration")
        self.bullet("Automation: n8n workflow automation, Go High Level (GHL) automation, lead enrichment pipelines")
        self.bullet("Web Development: WordPress, GHL web funnels, SEO-focused landing pages")
        self.bullet("Data Analytics: Data cleaning, sorting, analysis, and visualization")
        self.bullet("Database: SQL")
        self.bullet("Tools: Google Workspace, Canva, Git/GitHub")
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
        self.bullet("English for Immersive Environment (EIE) Department Representative \u00b7 University of Nueva C\u00e1ceres, 2020\u20132021")
        self.bullet("English for Immersive Environment (EIE) Student Assistant \u00b7 University of Nueva C\u00e1ceres, 2020\u20132021")
        self.bullet("Certificate of Recognition \u00b7 Relaytask, 2025")
        self.y += 4

    def _references(self):
        self.section_header("REFERENCES")
        self.bullet("Faith Villamor \u00b7 Registrar Clerk, University of Nueva Caceres \u00b7 09511644059 / villamorfaith@gmail.com")
        self.bullet("Mark Alfonso A. Cervantes \u00b7 Software Developer, Somisomi Franchise Ltd. \u00b7 0936 598 9544 / cmarkalfonso@yahoo.com")
        self.bullet("Samantha Espinas \u00b7 Network Engineer, Accenture \u00b7 09933075331")
        self.y += 8

    def _footer(self):
        self._ensure_space(40)
        self._put(MARGIN_L, self.y + SIZE_BODY, "I certify that the above information is true and correct.", False, SIZE_BODY, italic=True)
        self.y += 24
        self._put(MARGIN_L, self.y + SIZE_SECTION, "Piolo Rafael Avenido", True, SIZE_SECTION)


if __name__ == "__main__":
    builder = ResumeBuilder()
    builder.build()