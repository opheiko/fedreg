## Instructions

It is widely believed that some administrations have different focuses for their regulatory endeavors. The Federal Registrar contains a list of all of the proposed rules and final rules that government agencies issue to manage the US economy. Final rules are rules that have taken effect and present the true impact an administration has had on the regulatory structure.

As a result, our task is to understand how the administrations of George Bust and Barack Obama differed (if at all) in their regulatory emphasis. To do this, we use the Federal Register API to gather the rules made by both administrations. Specifically, the Federal Register Documents ‘search’ API (limited only to ‘final rules’ published issued after George Bush’s inauguration) yields a rich and simple dataset.

At a minimum, this project requires the implementation of a topic model of your choice on the ‘abstract’ field. It is not required but if you so choose, you may augment this core classification task by some of the following methods:

- Extracting information from the title

- Downloading the entire text of the rule and creating a topic model

- Performing entity extraction from the abstract and/or entire text of the rule to enhance the feature space

- Anything of interest in the data that you think would be of value

Following the creation of these features (both from the unstructured and structured portion of the data), a classifier needs to be built that distinguishes between rules made during these administrations. For any topics that show a high level of importance in distinguishing between the two administrations, please create a relevant chart(s) which show some descriptive statistics about these potential variables.

Please produce code with technical comments a Data Scientist could understand and a brief (1-2 page) and non-partisan written report a lay person could understand.

Please do not use any code from prior projects you have done. Only use code available on the internet (with citations in the comments) and code you personally produce.

At the conclusion of the report, please email all code and data (unless it’s too large to email) to Daniel Byler at dbyler@deloitte.com. We will promptly review your code and give you a response.