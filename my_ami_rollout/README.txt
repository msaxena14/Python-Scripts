Steps to be followed : 
1. get the name of asg                                                                                  Done
2. get the name / id of launchtemplate belonging to that asg                                            Done
3. create new launch template version from current default version                                      Done
4. get the minimum , maximum and desired count of the asg                                               Done 
5. --------------set scale in protection in all the instances--------------                             Done
        a. Increase desired by 1
        b. Decrease desired by 1
        c.calculate minimum healthy percentage = (100 - (1 / desired_count) X 100)
        d.put in the value of minimum healthy percentage in instance refresh
        e.initiate instance refresh

6. launch new instances one by one after the health check are passed (in target groups) {
    a. get the list of all newly launched inatances                                                     Done
    b. go for health check of newly launched instance as configured in the asg
    c. once received healthy move to next step else retry it untill {
        i. received healthy
        ii. if unhealthy: 
                if count < max_retries and reason == NotRegistedInTargetGroup:
                        add target in tg
                        healthcheck
                        
                else if count < max_retries and reason != NotRegistedInTargetGroup:
                        healthcheck
                        count = count + 1
}
7. now set scale in on newly launched instances and remove that from already exsisting one's
8. delete all the old instances