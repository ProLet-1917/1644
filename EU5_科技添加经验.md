# EU5 给国家添加科技的经验总结

**`unlock_advance_effect`** 仅解锁科技（可研究），不会应用科技效果。**`research_advance`** 才是完成研究并应用所有效果。

需要两步操作：先解锁，再研究。

```txt
every_country = {
	# 第一步：解锁科技
	unlock_advance_effect = { type = global_trade_advance }
	# 第二步：研究完成科技
	research_advance = advance_type:global_trade_advance
}
```

