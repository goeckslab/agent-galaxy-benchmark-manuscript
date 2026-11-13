-- Use each figure's native artwork for paginated and browser output.
function Image(image)
  if image.src:match("benchmark_results_summary/.+/output/.+%.png$") then
    if quarto.doc.is_format("latex") or quarto.doc.is_format("pdf") then
      image.src = image.src:gsub("%.png$", ".pdf")
    elseif quarto.doc.is_format("html") then
      image.src = image.src:gsub("%.png$", ".svg")
    end
  end
  return image
end
