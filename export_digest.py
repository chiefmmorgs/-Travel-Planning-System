from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sys
import asyncio
sys.path.insert(0, 'src')
from travel_agent_roma import SentientTravelAgent

async def export_to_pdf():
    agent = SentientTravelAgent()
    agent.add_trip("Barcelona", "2026-05-01", "2026-05-08", 2500)
    
    digest = await agent.generate_weekly_digest()
    
    # Create PDF
    doc = SimpleDocTemplate("travel_digest.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph("🌍 Your Weekly Travel Digest", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    content = Paragraph(
        digest['digest']['recommendations'].replace('\n', '<br/>'),
        styles['BodyText']
    )
    story.append(content)
    
    doc.build(story)
    print("✅ PDF saved as travel_digest.pdf")

asyncio.run(export_to_pdf())
