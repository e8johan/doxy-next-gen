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

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])


# === EXPERIMENT ===
#
# Iterate over the file contents linearly. 
# Store each comment block together with the token that it refers to.
# Notice that the token stored is most likely only a subset of the element that
# is described. The entire element will be extracted during the recursive 
# traversal that follows.
#

comments = []
class Comment:
    def __init__(self):
        self.comment_block = None    # The comment block in question
        self.sub_location = None     # The location of a token being referenced, not the entire element, just a token
        self.extent = None           # The extent of the element being referenced
        self.element_spelling = None # The text of the element being referenced
        self.qualified_name = None   # The fully qualified name of the element being referenced
        
    def __str__(self):
        return "'" + self.comment_block + "' at " + str(self.sub_location)

previous_token = None
comment_block = None
for token in tu.get_tokens(extent=tu.cursor.extent):
    if token.kind == clang.cindex.TokenKind.COMMENT:
        if comment_block:
            comment_block += "\n" + token.spelling
        else:
            comment_block = token.spelling
    else: # Not a comment
        if comment_block:
            comment = Comment()
            comment.comment_block = comment_block
            
            # TODO how to detect and treat freestanding blocks?
            # TODO how to detect and treat back references?
            # if should be back referenced
            #     comment.sub_extent = previous_token.location
            # else:
            comment.sub_location = token.location
            comments.append(comment)
            
            comment_block = None
        
        previous_token = token

if comment_block:
    comment = Comment()
    comment.comment_block = comment_block
    
    # TODO what is the block referring to?
    comment.sub_location = previous_token.location
    comments.append(comment)
    
for c in comments:
    print(c)
print("=== end of comments ===")

# Conclusions:
# - Each block of comments is is extracted.
# - We have a likely location of a single token in the described element.

# === EXPERIMENT ===
#
# Recursive, visitor based, parsing
#

def comment_from_extent(extent):
    # The extent of a cursor includes the whole element. This means that a 
    # class declaration contains all comments inside the body.
    # For this reason, the heusteristics is to pick the earliest comment block
    # matching, if multiple comment block locations match.
    
    res = None
    for c in comments:
        after = False
        before = False
        
        if c.sub_location.line > extent.start.line:
            after = True
        elif c.sub_location.line == extent.start.line and c.sub_location.column >= extent.start.column:
            after = True
            
        if c.sub_location.line < extent.end.line:
            before = True
        elif c.sub_location.line == extent.end.line and c.sub_location.column <= extent.end.column:
            before = True
            
        if after and before:
            if res:
                if res.sub_location.line > c.sub_location.line:
                    res = c
                elif res.sub_location.line == c.sub_location.line and res.sub_location.column > c.sub_location.column:
                    res = c
            else:
                res = c
        
    return res

def fully_qualified_name(cursor):
    if cursor is None:
        return ""
    elif cursor.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        return ""
    else:
        return "::".join(filter(None, [fully_qualified_name(cursor.semantic_parent), cursor.spelling]))        

def traverse(cursor, indent):
    if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
        c = comment_from_extent(cursor.extent)
        if c:
            c.qualified_name = fully_qualified_name(cursor)
            print("Comment: '" + c.comment_block + "' describes method " + c.qualified_name)
        else:
            print(fully_qualified_name(cursor) + " is not described")
    elif cursor.kind == clang.cindex.CursorKind.CONSTRUCTOR:
        c = comment_from_extent(cursor.extent)
        if c:
            c.qualified_name = fully_qualified_name(cursor)
            print("Comment: '" + c.comment_block + "' describes ctor " + c.qualified_name)
        else:
            print(fully_qualified_name(cursor) + " is not described")
    elif cursor.kind == clang.cindex.CursorKind.CLASS_DECL:
        c = comment_from_extent(cursor.extent)
        if c:
            c.qualified_name = fully_qualified_name(cursor)
            print("Comment: '" + c.comment_block + "' describes class " + c.qualified_name)
        else:
            print(fully_qualified_name(cursor) + " is not described")
    else: # Let's just ignore the rest for now...
        pass
    
    # TODO
    # extent
    # access_specifier
    # element spelling
    
    for child in cursor.get_children():
        traverse(child, indent+1)

traverse(tu.cursor, 0)

# Conclusions:
# - Comments can be associated with elements
# - Further data can be extracted
