November 12 Meeting

- Understand the project and how to analyze data from EEG
  - https://mne.tools/stable/generated/mne.filter.construct_iir_filter.html
  - https://arxiv.org/abs/2607.16647 
   --> EEG Preprocessing Pipeline explanation
  - https://www.researchgate.net/publication/398807533_EEG-Based_Focus_Analysis_to_Evaluate_the_Effectiveness_of_Active_Learning_Approaches
   --> research paper evaluating Learning using EEG observations. In this paper, focus is measured by memory retention,
       so it may not be applicable to MindGames. However, method section includes collection, pre-processing formula, score 
       calculation, and classification of EEG signal data, which we can draw inspiration from. Additionally, table 1 and 2
       show the average measurements of Alpha, Beta, Theta, Delta, Gamma waves of 20 students in a learning session. This can
       be an indicator of wave measurements when we design our focus index in MindGames.
  - https://nhahealth.com/brainwaves-the-language/
   --> useful website that summarizes each brain wave the EEG can capture, its frequencies, and affiliated physical states
       

    
- Next meeting on Tuesday 4 - 5 PM


What we discussed in 11.17 Meeting:
Proposed Plan for EEG Signal Processing:

1 Set up device (channels)

2 Clean data

3 Seperate waves 
 --> maybe do something with range? encoding

4 Create Movement Index
 --> maybe agitated/relax waves correspond to certain ball movement

- Next meeting on Tuesday 4-5 online
