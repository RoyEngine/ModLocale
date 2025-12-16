package second_in_command.skills.starfaring

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.BaseCampaignEventListener
import com.fs.starfarer.api.campaign.CargoAPI
import com.fs.starfarer.api.campaign.FleetEncounterContextPlugin
import com.fs.starfarer.api.campaign.comm.IntelInfoPlugin
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.fleet.FleetMemberAPI
import com.fs.starfarer.api.impl.campaign.DModManager
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.ids.Tags
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin
import com.fs.starfarer.api.impl.campaign.skills.FieldRepairsScript
import com.fs.starfarer.api.ui.SectorMapAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import com.fs.starfarer.api.util.WeightedRandomPicker
import second_in_command.SCData
import second_in_command.SCUtils
import second_in_command.misc.baseOrModSpec
import second_in_command.specs.SCBaseSkillPlugin
import java.awt.Color

class ContinuousRepairs : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("根据舰船级别，我方舰船被击沉后有 60%%/60%%/40%%/30%% 的概率避免 D-插件 的产生", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("每累计消灭 240 部署点的敌舰，从随机一艘舰船上移除一个 D-插件", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 被击溃的{主力舰}计为{双倍}点数", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "主力舰", "双倍")
        tooltip.addPara("   - 该效果在一场战斗中可以触发多次", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 消灭计数会在不同战斗场次间累积", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 忽略具有{坚固结构}船插的舰船", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "坚固结构")

    }

   /* override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        when (hullSize) {
            ShipAPI.HullSize.FRIGATE -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0f)
            ShipAPI.HullSize.DESTROYER -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0f)
            ShipAPI.HullSize.CRUISER -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0f)
            ShipAPI.HullSize.CAPITAL_SHIP -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0f)
        }

    }*/

    override fun callEffectsFromSeparateSkill(stats: MutableShipStatsAPI?, hullSize: ShipAPI.HullSize?, id: String?) {
        when (hullSize) {
            ShipAPI.HullSize.FRIGATE -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0.4f)
            ShipAPI.HullSize.DESTROYER -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0.4f)
            ShipAPI.HullSize.CRUISER -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0.6f)
            ShipAPI.HullSize.CAPITAL_SHIP -> stats!!.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 0.7f)
            else -> null
        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {

    }

    override fun onActivation(data: SCData) {
        if (data.isPlayer) {
            if (Global.getSector().allListeners.none { it is ContinuousRepairsListener }) {
                Global.getSector().addListener(ContinuousRepairsListener())
            }
        }
    }

    override fun onDeactivation(data: SCData) {
        if (data.isPlayer) {
            var listeners = Global.getSector().allListeners.filter { it is ContinuousRepairsListener }
            for (listener in ArrayList(listeners)) {
                Global.getSector().removeListener(listener)
            }
        }
    }

}


class ContinousIntel(var pick: FleetMemberAPI, var specId: String) : BaseIntelPlugin() {

    init {
        Global.getSector().addScript(this)
        endAfterDelay(14f)
    }

    override fun notifyEnded() {
        Global.getSector().removeScript(this)
    }

    override fun getName(): String {
        return "技能 - 持久维修"
    }

    override fun getIcon(): String {
        return "graphics/secondInCommand/starfaring/continuous_repairs.png"
    }

    override fun hasSmallDescription(): Boolean {
        return false
    }

    override fun addBulletPoints(info: TooltipMakerAPI?, mode: IntelInfoPlugin.ListInfoMode?, isUpdate: Boolean, tc: Color?, initPad: Float) {
        var spec = Global.getSettings().getHullModSpec(specId)
        info!!.addPara("${pick.shipName} - 已修复 ${spec.displayName}", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "${spec.displayName}")
    }

    override fun getTitleColor(mode: IntelInfoPlugin.ListInfoMode?): Color {
        return Misc.getBasePlayerColor()
    }

    override fun getIntelTags(map: SectorMapAPI?): MutableSet<String> {
        var tags = super.getIntelTags(map)
        tags.add("Skills")
        return tags
    }
}

class ContinuousRepairsListener() : BaseCampaignEventListener(false) {

    var required = 240

    override fun reportEncounterLootGenerated(plugin: FleetEncounterContextPlugin?, loot: CargoAPI?) {
        if (plugin == null) return

        if (plugin.battle.isPlayerSide(plugin.battle.getSideFor(plugin.winner))) {
            var dp = SCUtils.getSectorData().continiousRepairsDPSoFar

            for (data in plugin.loserData.ownCasualties) {
                dp += data.member.deploymentPointsCost
                if (data.member.isCapital) dp += data.member.deploymentPointsCost
            }

            while (dp >= required) {
                dp -= required

                var picks = WeightedRandomPicker<FleetMemberAPI>()
                for (member in Global.getSector().playerFleet.fleetData.membersListCopy) {
                    if (member.variant.hasDMods() && !member.variant.hasHullMod("rugged") && !member.baseOrModSpec().hasTag(Tags.HULL_UNRESTORABLE) && !member.variant.hasTag(Tags.VARIANT_UNRESTORABLE)) {
                        picks.add(member)
                    }
                }

                var pick = picks.pick()
                if (pick != null) {

                    var dmodSpecs = Global.getSettings().allHullModSpecs.filter { it.hasTag(Tags.HULLMOD_DMOD) }

                    var hmods = pick.variant.permaMods + pick.variant.hullMods

                    var foundDmods = ArrayList<String>()
                    for (hmod in hmods) {
                        if (dmodSpecs.map { it.id }.contains(hmod)) {
                           foundDmods.add(hmod)
                        }
                    }

                    var hmodPick = foundDmods.randomOrNull()
                    if (hmodPick != null && pick.variant != null) {
                        DModManager.removeDMod(pick.variant, hmodPick)

                        val spec = DModManager.getMod(hmodPick)
                        /*val intel = MessageIntel(pick.shipName + " - repaired " + spec.displayName,
                            Misc.getBasePlayerColor())
                        intel.icon = Global.getSettings().getSpriteName("intel", "repairs_finished")
                        Global.getSector().campaignUI.addMessage(intel, MessageClickAction.REFIT_TAB, pick)*/


                        //Intel
                        var intel = ContinousIntel(pick, spec.id)

                        Global.getSector().intelManager.addIntel(intel)

                        //Restore Visuals
                        val remainingdmods = DModManager.getNumDMods(pick.variant)
                        if (remainingdmods <= 0) {
                            FieldRepairsScript.restoreToNonDHull(pick.variant)
                        }
                    }
                }
            }

            SCUtils.getSectorData().continiousRepairsDPSoFar = dp
        }

    }


}