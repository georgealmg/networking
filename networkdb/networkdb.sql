use networkdb;

SELECT 
    l3.ip,
    l2.sw,
    l2.interface,
    l2.mac,
    dns.dns
FROM
    l3
        INNER JOIN
    l2 USING (joinkey)
        LEFT JOIN
    dns ON l3.ip = dns.ip;
    

SELECT 
    l3.ip,
    aci.sw,
    aci.interface,
    aci.mac,
    ifnull(dns.dns,"--") as dns
FROM
    l3
        INNER JOIN
    aci USING (joinkey)
        LEFT JOIN
    dns ON l3.ip = dns.ip; 