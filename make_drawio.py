import xml.sax.saxutils as saxutils

mermaid1 = '''classDiagram
    class FastAPIBackend {
        +get /()
        +get /health()
        +get /keywords()
        +get /history()
        +delete /history()
        +delete /history/{id}()
        +post /analyze(audio, custom_keywords) AnalysisResponse
        +post /analyze-demo(transcript) AnalysisResponse
    }

    class WhisperModel {
        +transcribe(audio_path) Tuple~segments, info~
    }

    class AnalysisResponse {
        +String filename
        +String language
        +Float duration_seconds
        +String transcript
        +String highlighted_transcript
        +List~KeywordStat~ matched_keywords
        +Int total_dangerous_keyword_hits
        +Int safety_score
        +String safety_level
        +List~SegmentOut~ segments
    }

    class HistoryItem {
        +String id
        +String created_at
        +String source_type
        +String filename
        +String language
        +Float duration_seconds
        +String transcript
        +List~KeywordStat~ matched_keywords
        +Int total_dangerous_keyword_hits
        +Int safety_score
        +String safety_level
    }

    class KeywordStat {
        +String keyword
        +Int count
    }

    class SegmentOut {
        +Float start
        +Float end
        +String text
    }

    class ReactFrontend {
        <<Vite SPA>>
        +App.jsx
        +Layout.jsx
        +HomePage.jsx
        +AboutPage.jsx
        +FAQPage.jsx
    }

    FastAPIBackend --> AnalysisResponse : Returns
    FastAPIBackend --> HistoryItem : Reads / Writes
    FastAPIBackend --> WhisperModel : Uses (Faster-Whisper)
    
    AnalysisResponse *-- KeywordStat : includes
    AnalysisResponse *-- SegmentOut : includes
    HistoryItem *-- KeywordStat : includes
    
    ReactFrontend --> FastAPIBackend : HTTP Requests
'''

mermaid2 = '''flowchart TD
    subgraph Frontend [React Frontend Vite]
        App[App.jsx] --> Layout[Layout.jsx]
        Layout --> Home[HomePage.jsx]
        Layout --> About[AboutPage.jsx]
        Layout --> FAQ[FAQPage.jsx]
    end

    subgraph Backend [FastAPI Backend]
        API[FastAPI Routes: main.py]
        Whisper[Faster-Whisper Model]
        JSONDB[(data/analysis_history.json)]
    end

    Home -->|POST /analyze Upload or Record| API
    Home -->|GET /history Fetch logs| API
    
    API -->|1. Transcribe Audio| Whisper
    Whisper -.->|2. Return Segments| API
    
    API <-->|3. Save / Load History| JSONDB
    
    API -.->|4. Return AnalysisResponse| Home
'''

xml_content = """<mxfile host="app.diagrams.net" modified="2023-11-20T17:15:28.988Z" agent="Mozilla/5.0" version="22.1.3">
  <diagram id="class-diagram" name="Class Diagram">
    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="1400" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="" style="shape=mermaid;align=center;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="1000" height="800" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
  <diagram id="architecture-diagram" name="Architecture">
    <mxGraphModel dx="1000" dy="1000" grid running="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1000" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0_2" />
        <mxCell id="1_2" parent="0_2" />
        <mxCell id="3" value="" style="shape=mermaid;align=center;" vertex="1" parent="1_2">
          <mxGeometry x="40" y="40" width="800" height="600" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

m1_escaped = saxutils.escape(mermaid1)
m2_escaped = saxutils.escape(mermaid2)

xml_content = xml_content.replace('id="2" value=""', f'id="2" value="{m1_escaped}"')
xml_content = xml_content.replace('id="3" value=""', f'id="3" value="{m2_escaped}"')

with open('code_explorer_uml.drawio', 'w', encoding='utf-8') as f:
    f.write(xml_content)
