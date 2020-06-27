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

class Comment:
    def __init__(self):
        self.comment_block = None    # The comment block in question
        self.sub_location = None     # The location of a token being referenced, not the entire element, just a token
        self.extent = None           # The extent of the element being referenced
        self.element_spelling = None # The text of the element being referenced
        self.qualified_name = None   # The fully qualified name of the element being referenced
        
    def __str__(self):
        return self.qualified_name + ":\n\n" + str(self.comment_block) + "\n\n---\n"

def is_start_of_comment_block(c):
    comment = c.strip()
    starts = ['/**', '/*!', '/*<', '///', '//!', '//<']
    for s in starts:
        if comment.startswith(s):
            return True
    return False

def is_back_reference_comment(c):
    # Assumes that it is a comment start
    
    comment = c.strip()
    starts = ['/*<', '//<']
    for s in starts:
        if comment.startswith(s):
            return True
    return False

def extract_comments(tu):
    res = []
    previous_token = None
    comment_block = None
    for token in tu.get_tokens(extent=tu.cursor.extent):
        if token.kind == clang.cindex.TokenKind.COMMENT:
            if comment_block:
                comment_block += "\n" + token.spelling
            elif is_start_of_comment_block(token.spelling):
                comment_block = token.spelling
                
            # TODO ensure that comment blocks are continous and do not contain empty lines
        else: # Not a comment
            if comment_block:
                comment = Comment()
                comment.comment_block = comment_block
                
                # TODO how to detect and treat freestanding blocks?
                if is_back_reference_comment(comment.comment_block):
                    if previous_token:
                        comment.sub_location = previous_token.location
                    else:
                        print("WARNING: comment '" + comment.comment_block + "' does not have anything to reference back to.")
                else:
                    comment.sub_location = token.location

                res.append(comment)
                
                comment_block = None
            
            previous_token = token

    if comment_block:
        comment = Comment()
        comment.comment_block = comment_block
        
        if is_back_reference_comment(comment.comment_block):
            if previous_token:
                comment.sub_location = previous_token.location
            else:
                print("WARNING: comment '" + comment.comment_block + "' does not have anything to reference back to.")
        else:
            print("WARNING: comment '" + comment.comment_block + "' does not have anything to reference forward to.")

        res.append(comment)
        
    return res

def comment_from_extent(extent):
    # The extent of a cursor includes the whole element. This means that a 
    # class declaration contains all comments inside the body.
    # For this reason, the heusteristics is to pick the earliest comment block
    # matching, if multiple comment block locations match.
    
    res = None
    for c in comments:
        if c.sub_location:
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

def traverse(cursor, comments):
    if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
        c = comment_from_extent(cursor.extent)
        if not c:
            # Add undescribed element to model
            c = Comment()
            comments.append(c)
        c.qualified_name = fully_qualified_name(cursor)
    elif cursor.kind == clang.cindex.CursorKind.CONSTRUCTOR:
        c = comment_from_extent(cursor.extent)
        if not c:
            # Add undescribed element to model
            c = Comment()
            comments.append(c)
        c.qualified_name = fully_qualified_name(cursor)
    elif cursor.kind == clang.cindex.CursorKind.CLASS_DECL:
        c = comment_from_extent(cursor.extent)
        if not c:
            # Add undescribed element to model
            c = Comment()
            comments.append(c)
        c.qualified_name = fully_qualified_name(cursor)
    else: # Let's just ignore the rest for now...
        pass
    
    # TODO extract these
    # actual extent
    # access_specifier
    # element spelling
    
    # TODO what to do about next level parsing, e.g. argument names
    
    for child in cursor.get_children():
        traverse(child, comments)

# TODO introduce a type for each comment block, e.g. class, namespace, method, constructor, function, enum, type, etc
# TODO collapse the model, e.g. if an element is found to be undescribed, but is described by an external block, ensure that the Comment items are merged

if __name__ == '__main__':
    index = clang.cindex.Index.create()
    tu = index.parse(sys.argv[1])

    comments = extract_comments(tu)
    traverse(tu.cursor, comments)
    
    for c in comments:
        print(str(c))
