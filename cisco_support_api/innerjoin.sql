use ciscoapi;
SELECT 
    devices.*, products.ProductReleaseDate,eox.EndOfSaleDate,software.ImageName
FROM
    devices
        INNER JOIN
    products ON devices.model = products.Productid
        INNER JOIN
    eox ON devices.model = eox.Productid
        INNER JOIN
    software ON devices.model = software.Productid;
    

use ciscoapi;
SELECT 
    devices.*, products.ProductSeries
FROM
    devices
        INNER JOIN
    products ON devices.Model = products.ProductID;