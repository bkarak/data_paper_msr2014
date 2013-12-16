#!/usr/bin/env ruby

require 'json'
require 'zlib'
require 'pp'

file = ARGV[0] || fail("No file to parse")

STDERR.puts "Reading file #{file}"

f = File.open(file)
gz = Zlib::GzipReader.new(f).read
js = JSON.parse(gz)

STDERR.puts "Building graph"

graph = js.map do |e|
  e[1]['dependencies '].map do |d|
    [e[0], d]
  end
end.flat_map { |i| i }

STDERR.puts "Build graph - number of edges: #{graph.size}"
STDERR.puts "Collecting all versions for all artifacts"
all_versions = js.reduce(Hash.new { |hash, key| hash[key] = [] }) do |acc, e|
  group, artifact, version = e[0].split(/\|\|/)

  if e[1]['version_order'].nil?
    STDERR.puts "Name: #{e[0]} no version order"
  else
    acc["#{group}.#{artifact}"] << [version, e[1]['version_order']]
  end
  acc
end

STDERR.puts "Computing the latest version for each artifact"
latest_versions = all_versions.reduce(Hash.new {}) do |acc, e|
  k = e[0]
  v = e[1]
  max_version = v.max { |a, b| a[1] <=> b[1] }
  acc[k] = max_version[0]
  acc
end

STDERR.puts "Resolving dependency versions"
processed = resolved = not_found = 0
graph = graph.reduce([]) do |acc, edge|
  processed += 1
  group, artifact, version = edge[1].split(/\|\|/)
  name = "#{group}.#{artifact}"

  if version.nil?
    latest = latest_versions[name]

    if latest.nil?
      not_found += 1
      acc
    else
      resolved += 1
      acc << [edge[0], "#{group}||#{artifact}||#{latest}"]
    end
  else
    version_exists = all_versions[name].find { |v| v[0] == version }.nil?
    unless version_exists
      acc << edge
    else
      #STDERR.puts "#{}"
      not_found += 1
      acc
    end
  end

  STDERR.print "\rProcessed: #{processed}, resolved: #{resolved},",
               " unresolved: #{not_found}, ",
               "no resolution needed: #{processed - resolved - not_found}"
  acc
end

STDERR.puts
STDERR.puts "Resolved versions - number of edges: #{graph.size}"

STDERR.puts "Saving adjacency matrix to run pagerank on"
pr_file = File.open("pr.txt", 'w')
graph.each do |connection|
  pr_file.print connection[0], " => ", connection[1], "\n"
end
pr_file.close

STDERR.puts "Running pagerank -- needs to be in $PATH"
system "pagerank pr.txt 2>/dev/null > pr-result.txt"

STDERR.puts "Reading pagerank results"
pr_results = File.open("pr-result.txt").map do |line|
  #format: com.cedarsoft.commons||mail||1.4.0 = 5.77094558229626e-06
  node, pr = line.split(/\=/).map { |x| x.strip }
  [node, pr.to_f]
end

STDERR.puts "Calculating number of incoming connections per node"
incoming = graph.map { |e| e[1] }.reduce(Hash.new(0)) { |acc, i|
  acc[i] += 1
  acc
}

puts "artifact,pagerank,incoming_connections,is_latest"
pr_results.sort { |a, b| b[1] <=> a[1] }.each { |l|

  def is_latest_version(versions, item, ver)
    group, artifact, version = item.split(/\|\|/)
    name = "#{group}.#{artifact}"
    latest = versions[name]
    if ver == latest then true else false end
  end

  group, artifact, version = l[0].split(/\|\|/)
  print l[0], ",",
        l[1], ",",
        if incoming[l[0]].nil? then 0 else incoming[l[0]] end, ",",
        is_latest_version(latest_versions, l[0], version), "\n"
}

STDERR.puts "Clean up"
File.delete("pr-result.txt")
File.delete("pr.txt")