-- _filters/hreflang.lua
-- Inject <link rel="canonical"> on every page, plus <link rel="alternate" hreflang="...">
-- tags when the page has a mirrored counterpart under ja/ or en/.

local SITE_URL = "https://notes.iwase.dev"

local function file_exists(path)
  local f = io.open(path, "r")
  if f then f:close(); return true end
  return false
end

local function project_directory(input)
  if quarto.project and quarto.project.directory then
    return quarto.project.directory
  end

  -- `quarto preview path/to/page.qmd` first renders the document without
  -- project metadata. Walk up from the absolute input path in that case.
  local dir = pandoc.path.directory(input)
  while dir do
    if file_exists(pandoc.path.join({ dir, "_quarto.yml" })) then return dir end
    local parent = pandoc.path.directory(dir)
    if parent == dir then break end
    dir = parent
  end
  return pandoc.system.get_working_directory()
end

-- Map a project-relative .qmd path to the URL Cloudflare Pages serves.
-- Pages strips ".html" and serves "index" as the directory path with a trailing slash.
local function url_for(rel)
  local p = rel:gsub("%.qmd$", "")
  if p == "index" then return SITE_URL .. "/" end
  return SITE_URL .. "/" .. p:gsub("/index$", "/")
end

function Pandoc(doc)
  local input = pandoc.path.normalize(quarto.doc.input_file)
  local project = pandoc.path.normalize(project_directory(input)):gsub("/$", "") .. "/"
  local rel = input:sub(1, #project) == project and input:sub(#project + 1) or input

  if rel == "404.qmd" then return doc end

  local self_url = url_for(rel)
  local out = { string.format('<link rel="canonical" href="%s">', self_url) }

  local lang = rel:match("^(ja)/") or rel:match("^(en)/")
  if lang then
    local other = (lang == "ja") and "en" or "ja"
    local other_rel = other .. rel:sub(#lang + 1)
    if file_exists(project .. other_rel) then
      local other_url = url_for(other_rel)
      local x_default = (lang == "en") and self_url or other_url
      local alt = '<link rel="alternate" hreflang="%s" href="%s">'
      table.insert(out, string.format(alt, lang, self_url))
      table.insert(out, string.format(alt, other, other_url))
      table.insert(out, string.format(alt, "x-default", x_default))
    end
  end

  quarto.doc.include_text("in-header", table.concat(out, "\n"))
  return doc
end
