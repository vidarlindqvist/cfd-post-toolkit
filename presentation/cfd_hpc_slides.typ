// tokyonight theme...

#let bg     = rgb("#1a1b26")
#let fg     = rgb("#c0caf5")
#let blue   = rgb("#7aa2f7")
#let muted  = rgb("#565f89")
#let border = rgb("#414868")

#set page(width: 33.867cm, height: 19.05cm, fill: bg, margin: 0pt)
#set text(font: "JetBrainsMono NF", fill: fg)

// Slide 1... title
#align(center + horizon)[
  #text(size: 160pt, weight: "bold", fill: blue)[CFD]
  #v(0.6cm)
  #text(size: 28pt, fill: muted)[2026-09-15]
]

#pagebreak()

// Slide 2... HPC
#align(center + horizon)[
  #text(size: 160pt, weight: "bold", fill: blue)[HPC]
]

#pagebreak()

// Slide 3... case conditions
#align(center + horizon)[
  #text(size: 100pt, weight: "bold", fill: blue)[Högfartspunkt]
  #v(0.6cm)
  #text(size: 28pt, fill: muted)[M 1.6  ·  1° AoA  ·  10,000 m ALT]
]

#pagebreak()

// Slide 4... hinge moment coefficient convergence
#align(center + horizon)[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1cm,
    align(center + horizon)[
      #image("/fluent/Ch_upper_flap_convergence.png", width: 100%)
    ],
    align(center + horizon)[
      #image("/fluent/Ch_lower_flap_convergence.png", width: 100%)
    ],
  )
]

#pagebreak()

// Result slides...
#let image-slide(path) = align(center + horizon)[
  #image(path, width: 90%)
]

#let captioned-image-slide(path, caption) = align(center + horizon)[
  #block(width: 90%)[
    #image(path, width: 100%)
    #v(0.4cm)
    #align(left)[
      #text(size: 16pt, fill: muted)[#caption]
    ]
  ]
]

// Slide 5... Cp
#image-slide("Cp.png")

#pagebreak()

// Slide 6... Streamlines 1
#captioned-image-slide("Streamlines1.png", "streamlines colored by velocity")

#pagebreak()

// Slide 7... Streamlines 2
#captioned-image-slide("Streamlines2.png", "streamlines colored by velocity")

#pagebreak()

// Slide 8... Q-criterion 1
#captioned-image-slide("Qcrit1.png", "Q Criterion (Normalized) colored by velocity")

#pagebreak()

// Slide 9... Q-criterion 2
#captioned-image-slide("Qcrit2.png", "Q Criterion (Normalized) colored by velocity")
