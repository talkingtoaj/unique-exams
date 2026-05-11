
### Text strings you will use in the template exams to indicate the structure of the exam

# To indicate that the following paragraphs decribe one of the alternative questions, the preceeding paragraph should include this text
ALTERNATIVE_TEXT= "Question Alternate"

# Additional regular expressions that identify alternative question headings.
# These cover translated templates such as:
# - "2. Bölüm, Alternatif Soru 1"
# - "3.Bölüm, Alternatif soru 3"
# - "Bölüm 6, Alternatif Soru 2"
ALTERNATIVE_PATTERNS = [
    r"\balternatif\s+soru\s+\d+\b",
]

# To indicate the block of alternative questions is now over
END_ALTERNATIVES= "END ALTERNATES"

# Additional regular expressions that identify the end of an alternative block.
END_ALTERNATIVE_PATTERNS = [
    r"\balternatif\s+sonu\b",
]

# Used to obfuscate the tokens used for unique exams. Not that important, but if you want to modify it, each number should be less than 5.
SEED = [0,2,1,3,0,1,2,0,3]
