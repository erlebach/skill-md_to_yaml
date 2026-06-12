"""Ad-hoc: measure two-column Mermaid SVG size vs available column height.

Usage: python tests/measure_two_col_mermaid.py /path/to/compiled.html
"""
import json
import sys

from playwright.sync_api import sync_playwright

url = "file://" + sys.argv[1]
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(url)
    page.wait_for_function(
        "document.querySelectorAll('.diagram-container[data-mermaid-pre] svg').length >= 2"
        " && document.querySelectorAll('.diagram-container.mermaid-pending').length === 0",
        timeout=30000,
    )
    page.wait_for_timeout(1000)
    data = page.evaluate(
        """() => {
        const out = [];
        document.querySelectorAll('.slide-two-column .diagram-container[data-mermaid-pre]').forEach(c => {
          const svg = c.querySelector('svg');
          if (!svg) return;
          const col = c.closest('.col-left, .col-right');
          const slide = c.closest('section');
          const texts = [...svg.querySelectorAll('text, span')]
            .map(t => parseFloat(getComputedStyle(t).fontSize)).filter(x => x > 0).sort((a, b) => a - b);
          out.push({
            slide: slide.querySelector('h2')?.textContent?.trim() || '',
            type: c.dataset.diagramType || '',
            svgH: Math.round(svg.getBoundingClientRect().height),
            panelH: Math.round(c.getBoundingClientRect().height),
            colH: Math.round(col ? col.getBoundingClientRect().height : 0),
            styleW: svg.style.width, styleH: svg.style.height,
            medianLabelPx: texts.length ? +texts[Math.floor(texts.length / 2)].toFixed(1) : 0,
          });
        });
        return out;
      }"""
    )
    print(json.dumps(data, indent=1))
    browser.close()
