# sequence-similarity
The file is my Python implementation for the algorithm which is depicted in the thesis - ["S²MP: Similarity Measure for Sequential Patterns"](http://crpit.com/confpapers/CRPITV87Saneifar.pdf)

It is completely based on the writing, and all naming of functions are coherent with it, so users who have read the article should not find big problems in usage. I have also implemented the weighted average for orderScore and AveWeightScore to calculate the final scores.

# Usage
You will need to define two sequences in list type, with strings inside representing the elements. The sequence on the left in the function call should be your base sequence.

Example:

M1 = ['a', 'b', 'c']

M2 = ['a','c']

model = S2MP()

model.fit(M1, M2)

print(model.SimDegree(0.1))

\# the result is 0.7700000000000001
