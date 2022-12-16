
This is a k8s cronjob for keeping our MailChimp list/tags updated.
User information and group memberships are pulled from OSGConnect
and Comanage APIs.

It is expected that a config file is bind mounted to 
`/srv/mailchimp-sync/mailchimp-sync.conf` . Example:

    [mailchimp]
    
    token = 
    
    [osgconnect]
    
    token = 
    
    [comanage]
    
    api_username = 
    api_password = 

It is also expected that a pv is bind mounted to
`/srv/mailchimp-sync/data`


