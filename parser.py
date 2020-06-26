#
#    doxy-next-gen - a documentation extractor and generator
#    Copyright (C) 2020 Johan Thelin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import sys
import clang.cindex

print(sys.argv)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])


# === EXPERIMENT ===
#
# Iterate over the file contents linearly. Could a state-machine be built from this?
#
for token in tu.get_tokens(extent=tu.cursor.extent):
    print(str(token.kind) + " / " + str(token.cursor.kind) + ": '" + str(token.spelling) + "' [" + str(token.location) + "]")
    
# Conclusions:
# - Each block of comments is very easy to extract.
# - How do we go about extracting the signature of documented elements
#   - The constructor consists of both CONSTRUCTOR and PARAM_DECL cursor types.
#   - The functions, CXX_METHOD and PARAM_DECL
#   - The out-of-class implementation of a function - CXX_METHOD, TYPE_REF, PARAM_DECL

# === EXPERIMENT ===
#
# Recursive, visitor based, parsing
#
def fully_qualified_name(cursor):
    if cursor is None:
        return ""
    elif cursor.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        return ""
    else:
        return "::".join(filter(None, [fully_qualified_name(cursor.semantic_parent), cursor.spelling]))
        

def traverse(cursor, indent):
    print(" "*indent + str(cursor.kind) + ": [" + str(cursor.location) + "] ")
    if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
        print(" "*(indent+2) + "|- " + cursor.spelling + " " + str(cursor.access_specifier))
        parts = []
        for token in tu.get_tokens(extent=cursor.extent):
            parts.append(token.spelling)
        print(" "*(indent+2) + "|- " + " ".join(parts))
        print(" "*(indent+2) + "+- " + fully_qualified_name(cursor))

    for child in cursor.get_children():
        traverse(child, indent+1)

traverse(tu.cursor, 0)

# Conclusions:
# - No comments visited
# - Can build fully qualified names
# - Can extract definition / signature (needs polish)
